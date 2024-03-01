import configparser
import json
import logging
import asyncio

from redis.asyncio import Redis

import traceback
from typing import Any

import disnake
import quart
import hypercorn

from hypercorn.asyncio import serve

# import sdc_api_py
from disnake.ext import commands
import api

from config import *

import pomice
from clients.database import Database
from utils.build import Build
from utils.embeds import type_embed
from utils.ex_load import *
from utils.printer import *


class NoirBot(commands.AutoShardedInteractionBot):
    """Кастомный класс Noir с включенными в него table, node и т.д."""

    def __init__(
            self,
            *,
            config: str = "noir.properties",
            debug: bool = False) -> None:
        # Debug or not
        self._debug = debug

        # Config
        self._config = configparser.ConfigParser()
        self._config.read(config)

        # Intents
        intents = disnake.Intents.default()
        intents.members = True

        # Sync flags
        sync = (
            commands.CommandSyncFlags.all()
            if (
                self._config.getboolean("launch", "sync_commands")
                if not self._debug
                else self._config.getboolean("altlaunch", "sync_commands")
            )
            else commands.CommandSyncFlags.none()
        )

        super().__init__(
            # sync_commands=True,
            command_sync_flags=sync,
            shard_count=self._config.getint("launch", "shard_count")
            if not self._debug
            else self._config.getint("altlaunch", "shard_count"),
            chunk_guilds_at_startup=False,
            status=disnake.Status.idle,
            activity=disnake.Activity(name="noirplayer.su", type=disnake.ActivityType.listening),
            intents=intents,
        )

        # Pool
        self._pool = pomice.NodePool()

        # MongoDB
        self._db = Database()

        # Redis
        self._redis = Redis(host=HOST, port=PORT, password=PASS)

        # Build util
        self._build = Build()

        # App server
        # self._app = setup(bot=self)

        # Jsons
        self._errors = json.load(
            open(
                "json-obj/errors.json",
                "r",
                encoding="utf-8"))
        self._hello = json.load(
            open(
                "embeds/hello.json",
                "r",
                encoding="utf-8"))
        self._help = json.load(open("embeds/help.json", "r", encoding="utf-8"))

        # Set logging
        logging.basicConfig(
            level=logging.INFO,
            filename="latest.log",
            filemode="w",
            format="%(asctime)s %(levelname)s %(message)s",
        )

        # Setup
        self.setup()

        # Connect lavalink
        self.loop.create_task(self.connect_nodes())

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Setup

    def setup(self):
        lprint("Loading cogs", Color.blue)

        cogsLoad(self)

        if self._config.getboolean("launch", "sdc_api_enabled"):
            lprint("Sending data to SD.C", Color.magenta)
            try:
                data = sdc_api_py.Bots(
                    self, self._config.get(
                        "tokens", "sdc_token"))
                data.create_loop()
            except BaseException:
                pass
            else:
                lprint("Loop created", Color.cyan)

        lprint("Done", Color.green)

    # -------------------------------------------------------------------------------------------------------------------------------------
    # App

    def serve_api(self):

        lprint("Loading FastAPI", Color.blue, worker="APP")

        self._app = api.__init__(bot=self)

        if not self._debug:
            config = hypercorn.Config()
            config.bind = ["0.0.0.0:5000"]
            config.use_reloader = True

            lprint("Run in prodaction", Color.green, worker="APP")

            asyncio.run(serve(self._app, config))

        else:
            config = hypercorn.Config()
            config.bind = ["0.0.0.0:5001"]
            config.use_reloader = True
            config.debug = True

            lprint("Run in debug", Color.green, worker="APP")

            asyncio.run(serve(self._app, config))

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Lavalink connection

    async def connect_nodes(self):
        """Connect to our Lavalink nodes."""
        lprint("Waiting for ready...", Color.magenta)

        await self.wait_until_ready()

        lprint("Starting nodes", Color.magenta)

        try:
            self._node = await self._pool.create_node(
                bot=self,
                host=self._config.get("lavapass", "host"),
                port=self._config.getint("lavapass", "port"),
                password=self._config.get("lavapass", "pass"),
                identifier="Noir",
                log_level=logging.INFO,
            )

        except Exception as e:
            return lprint(f"Node was not created: {e}", Color.red, "ERROR")

        lprint("Node created", Color.magenta)

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Events

    async def on_ready(self):
        lprint(f"Starting as {self.user} (ID: {self.user.id})", Color.magenta)

        lprint("Player is ready")

        logging.info("Player is ready")

        if not self.pool.node_count:
            return

        lprint("Checking for dead players...", Color.cyan, "CLEANER")

        for player in list(self.node.players.values()):
            if player.is_dead or not player.is_connected:
                try:
                    await player.destroy()
                except BaseException:
                    lprint(
                        f"Player {player} is not cleaned",
                        Color.cyan,
                        "CLEANER")

        lprint("Cleanup done", Color.cyan, "CLEANER")

    async def on_shard_connect(self, id):
        lprint(f"Player connected | {id}")
        logging.info(f"Player connected | {id}")

    async def on_slash_command_error(self, inter: disnake.Interaction, error):
        if error is commands.CommandError or error is commands.CommandInvokeError:
            e = self._errors.get(
                error.__cause__.__class__.__name__,
                "Неизвестная ошибка. Простите...")
        else:
            e = self._errors.get(
                error.__class__.__name__, "Неизвестная ошибка. Простите..."
            )
        await inter.send(
            embed=type_embed(
                "error", f"```diff\n- {e}```\n||```diff\n- {error}```||"
            ),  # \n*Исходное сообщение об ошибке*: ||```Текст: {error.__cause__}\nИмя ошибки: {error.__cause__.__class__.__name__}```||"),
            ephemeral=True,
            components=[
                disnake.ui.Button(
                    style=disnake.ButtonStyle.url,
                    label="report",
                    url="https://discord.gg/ua4kpgzpWJ",
                )
            ],
        )

        logging.error(f"error in cmd:")
        logging.error(traceback.format_exc())

    async def on_error(self, event_method: str, *args: Any, **kwargs: Any) -> None:
        lprint(f"Exception in event_method {event_method}", Color.red, "ERROR")
        traceback.print_exc()
        lprint(f"End of traceback", Color.red, "ERROR")

        logging.error(f"error:")
        logging.error(traceback.format_exc())

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Run & Stop

    def run(self) -> None:
        try:
            self.loop.run_until_complete(self.start())
        except KeyboardInterrupt:
            self.stop()
            # cancel all tasks lingering

    def start(self):
        if self._debug:
            return super().start(self._config.get("altsecrets", "token"))
        return super().start(self._config.get("secrets", "token"))

    async def stop(self) -> None:
        await self.node.disconnect()
        await self.close()
        self.loop.close()

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Extensions

    def exload(self, path: None | str = None) -> None:
        """Load extensions in `/cogs`"""
        cogsLoad(self) if not path else self.load_extension(path)

    def exreload(self, path: None | str = None) -> None:
        """Reload extensions in `/cogs`"""
        cogsReload(self) if not path else self.reload_extension(path)

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Properties

    @property
    def pool(self) -> pomice.NodePool:
        """pomice.NodePool"""
        return self._pool

    @property
    def node(self) -> pomice.Node:
        """pomice.Node"""
        return self._pool.get_node()

    @property
    def db(self) -> Database:
        """Database class"""
        return self._db

    @property
    def redis(self) -> Redis:
        """Redis class"""
        return self._redis

    @property
    def app(self) -> quart.Quart:
        """App class"""
        return self._app

    @property
    def build(self) -> Build:
        """Build class"""
        return self._build

    @property
    def errors(self) -> dict:
        """Errors dict"""
        return self._errors

    @property
    def help(self) -> dict:
        """Help embed dict"""
        return self._help

    @property
    def hello(self) -> dict:
        """Hello embed dict"""
        return self._hello
