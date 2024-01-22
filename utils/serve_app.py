from hypercorn.asyncio.run import *

def _share_socket(sock: socket) -> socket:
    # Windows requires the socket be explicitly shared across
    # multiple workers (processes).
    from socket import fromshare  # type: ignore

    sock_data = sock.share(getpid())  # type: ignore
    return fromshare(sock_data)

async def worker_serve(
    app,
    config,
    *,
    loop = None,
) -> None:
    config.set_statsd_logger_class(StatsdLogger)

    loop = asyncio.get_event_loop() if not loop else loop

    if shutdown_trigger is None:
        signal_event = asyncio.Event()

        def _signal_handler(*_: Any) -> None:  # noqa: N803
            signal_event.set()

        for signal_name in {"SIGINT", "SIGTERM", "SIGBREAK"}:
            if hasattr(signal, signal_name):
                try:
                    loop.add_signal_handler(getattr(signal, signal_name), _signal_handler)
                except NotImplementedError:
                    # Add signal handler may not be implemented on Windows
                    signal.signal(getattr(signal, signal_name), _signal_handler)

    #     shutdown_trigger = signal_event.wait  # type: ignore

    shutdown_trigger = asyncio.Event().wait
    # loop.add_signal_handler(signal.SIGBREAK, lambda: loop.stop())

    lifespan = Lifespan(app, config, loop)

    lifespan_task = loop.create_task(lifespan.handle_lifespan())
    await lifespan.wait_for_startup()
    if lifespan_task.done():
        exception = lifespan_task.exception()
        if exception is not None:
            raise exception

    if sockets is None:
        sockets = config.create_sockets()

    ssl_handshake_timeout = None
    if config.ssl_enabled:
        ssl_context = config.create_ssl_context()
        ssl_handshake_timeout = config.ssl_handshake_timeout

    context = WorkerContext()
    server_tasks: WeakSet = WeakSet()

    async def _server_callback(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        server_tasks.add(asyncio.current_task(loop))
        await TCPServer(app, loop, config, context, reader, writer)

    servers = []
    for sock in sockets.secure_sockets:
        if config.workers > 1 and platform.system() == "Windows":
            sock = _share_socket(sock)

        servers.append(
            await asyncio.start_server(
                _server_callback,
                backlog=config.backlog,
                ssl=ssl_context,
                sock=sock,
                ssl_handshake_timeout=ssl_handshake_timeout,
            )
        )
        bind = repr_socket_addr(sock.family, sock.getsockname())
        await config.log.info(f"Running on https://{bind} (CTRL + C to quit)")

    for sock in sockets.insecure_sockets:
        if config.workers > 1 and platform.system() == "Windows":
            sock = _share_socket(sock)

        servers.append(
            await asyncio.start_server(_server_callback, backlog=config.backlog, sock=sock)
        )
        bind = repr_socket_addr(sock.family, sock.getsockname())
        await config.log.info(f"Running on http://{bind} (CTRL + C to quit)")

    for sock in sockets.quic_sockets:
        if config.workers > 1 and platform.system() == "Windows":
            sock = _share_socket(sock)

        _, protocol = await loop.create_datagram_endpoint(
            lambda: UDPServer(app, loop, config, context), sock=sock
        )
        server_tasks.add(loop.create_task(protocol.run()))
        bind = repr_socket_addr(sock.family, sock.getsockname())
        await config.log.info(f"Running on https://{bind} (QUIC) (CTRL + C to quit)")

    tasks = []

    tasks.append(loop.create_task(raise_shutdown(shutdown_trigger)))

    try:
        if len(tasks):
            gathered_tasks = asyncio.gather(*tasks)
            await gathered_tasks
        else:
            pass
    except (ShutdownError, KeyboardInterrupt):
        pass
    finally:
        await context.terminated.set()

        for server in servers:
            server.close()
            await server.wait_closed()

        # Retrieve the Gathered Tasks Cancelled Exception, to
        # prevent a warning that this hasn't been done.
        gathered_tasks.exception()

        try:
            gathered_server_tasks = asyncio.gather(*server_tasks)
            await asyncio.wait_for(gathered_server_tasks, config.graceful_timeout)
        except asyncio.TimeoutError:
            pass
        finally:
            # Retrieve the Gathered Tasks Cancelled Exception, to
            # prevent a warning that this hasn't been done.
            gathered_server_tasks.exception()

            await lifespan.wait_for_shutdown()
            lifespan_task.cancel()
            await lifespan_task