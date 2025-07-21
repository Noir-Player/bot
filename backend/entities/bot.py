"""
Bot entity `commands.AutoShardedInteractionBot`
"""

import traceback
from os import listdir
from typing import Callable

import disnake
from _logging import get_logger
from disnake.ext import commands

from .config import get_instance as get_config
from .database import init as create_database
from .node import create_node


class NoirBot(commands.AutoShardedInteractionBot):
    """Bot entity `commands.AutoShardedInteractionBot`"""

    def __init__(self):
        super().__init__(intents=disnake.Intents.all())

        self._config = get_config()

        self._log = get_logger("bot")

        intents = disnake.Intents.default()
        intents.members = True

        command_sync_flag = (
            commands.CommandSyncFlags.default()
            if self._config.sync_commands
            else commands.CommandSyncFlags.none()
        )

        test_guilds = (
            [self._config.support_server_id]
            if self._config.mode == "dev" and self._config.support_server_id
            else None
        )

        super().__init__(
            command_sync_flags=command_sync_flag,
            shard_count=self._config.shard_count,
            intents=intents,
            activity=disnake.Activity(
                name=self._config.activity_name,
                type=self._config.activity_status,
            ),
            owner_id=self._config.owner_id,
            test_guilds=test_guilds,
        )

    # ----------------------------------------------------------------------------

    def run(self):
        try:
            self.loop.run_until_complete(self.start())
        except KeyboardInterrupt:
            pass  # TODO: add graceful shutdown
            # self.loop.run_until_complete(self.stop())
            # cancel all tasks lingering

    def start(self):  # type: ignore
        return super().start(self._config.token)

    async def stop(self):
        await self.close()
        self.loop.close()

    # ----------------------------------------------------------------------------

    @staticmethod
    def provide_cogs(directory: str = "./cogs"):
        def decorator(function: Callable):
            def wrapper(self, *args, **kwargs):
                curr, total = 1, len(listdir(directory))

                for filename in listdir(directory):
                    if filename.endswith(".py"):
                        function(self, filename, curr, total)

                    curr += 1

            return wrapper

        return decorator

    @provide_cogs()
    def load_extensions(self, filename: str = ..., curr: int = ..., total: int = ...):  # type: ignore
        """Load cogs from `./cogs` directory"""
        try:
            self.load_extension(f"cogs.{filename[:-3]}")
            self._log.info(f"cog {filename} load, {curr}/{total}")

        except Exception as error:  # something in cog wrong
            self._log.error(f"error in cog {filename}, {curr}/{total} | {error}")
            if self._config.mode == "dev":
                traceback.print_exc()

    @provide_cogs()
    def reload_extensions(self, filename: str = ..., curr: int = ..., total: int = ...):  # type: ignore
        """Reload cogs from `./cogs` directory"""
        try:
            self.reload_extension(f"cogs.{filename[:-3]}")
            self._log.info(f"cog {filename} reload, {curr}/{total}")

        except Exception as error:  # something in cog wrong
            self._log.error(f"error in cog {filename}, {curr}/{total} | {error}")

    # ----------------------------------------------------------------------------

    async def on_ready(self):
        self._log.info(f"Starting as {self.user} (ID: {self.user.id})")
        self._log.info("on_ready was called, creating node...")

        create_node_state = await create_node(self)

        if not create_node_state:
            return self._log.error("Node was not created 💔")

        self._log.info("Calling load_extensions...")

        self.load_extensions()

        if self._config.sync_commands:
            self._log.info("Syncing commands...")
            await self._sync_application_commands()
            self._log.info("Commands synced")

    # ----------------------------------------------------------------------------

    async def on_shard_connect(self, id):
        self._log.debug(f"Shard connected | {id}")

    # ----------------------------------------------------------------------------

    async def on_connect(self):
        self._log.info("on_connect was called, creating database")
        await create_database()

        self._log.info("Database ininted")


# =============================================================================

instance = None


def get_instance():
    """Singleton getter"""
    global instance
    if instance is None:
        instance = NoirBot()
    return instance
