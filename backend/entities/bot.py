"""
Bot entity `commands.AutoShardedInteractionBot`
"""

from os import listdir
from typing import Callable

import disnake
from _logging import get_logger
from disnake.ext import commands

from .config import get_instance as get_config


class NoirBot(commands.AutoShardedInteractionBot):
    """Bot entity `commands.AutoShardedInteractionBot`"""

    def __init__(self):
        super().__init__(intents=disnake.Intents.all())

        self._config = get_config()

        self._log = get_logger("bot")

        intents = disnake.Intents.default()
        intents.members = True

        command_sync_flag = (
            commands.CommandSyncFlags.all()
            if self._config.sync_commands
            else commands.CommandSyncFlags.none()
        )

        super().__init__(
            command_sync_flags=command_sync_flag,
            shard_count=self._config.shard_count,
            intents=intents,
            activity=disnake.Activity(
                name=self._config.activity_name,
                type=self._config.activity_status,
            ),
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
                curr, total = 1, len(listdir(directory)) - 1

                for filename in listdir(directory):
                    if filename.endswith(".py"):
                        function(self, filename, curr, total)

                    curr += 1

            return wrapper

        return decorator

    @provide_cogs()
    def load_extensions(self, filename: str, curr: int, total: int):  # type: ignore
        """Load cogs from `./cogs` directory"""
        try:
            self.load_extension(f"cogs.{filename[:-3]}")
            self._log.info(f"cog {filename} load, {curr}/{total}")

        except Exception as error:  # something in cog wrong
            self._log.error(f"error in cog {filename}, {curr}/{total} | {error}")

    @provide_cogs()
    def reload_extensions(self, filename: str, curr: int, total: int):
        """Reload cogs from `./cogs` directory"""
        try:
            self.reload_extension(f"cogs.{filename[:-3]}")
            self._log.info(f"cog {filename} reload, {curr}/{total}")

        except Exception as error:  # something in cog wrong
            self._log.error(f"error in cog {filename}, {curr}/{total} | {error}")


# =============================================================================

instance = None


def get_instance():
    """Singleton getter"""
    global instance
    if instance is None:
        instance = NoirBot()
    return instance
