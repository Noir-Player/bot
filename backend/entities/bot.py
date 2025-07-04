"""
Bot entity `commands.AutoShardedInteractionBot`
"""

from os import listdir

import disnake
from config import get_instance as get_config
from disnake.ext import commands

from .._logging import get_logger


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

    def start(self):
        return super().start(self._config.token)

    async def stop(self):
        await self.close()
        self.loop.close()

    # ----------------------------------------------------------------------------

    def load_extensions(self):
        curr, total = 1, len(listdir("./cogs")) - 1

        for filename in listdir("./cogs"):
            if filename.endswith(".py"):
                try:  # load cog
                    self.load_extension(f"cogs.{filename[:-3]}")
                    self._log.info(f"cog {filename} load, {curr}/{total}")

                except Exception as error:  # something in cog wrong
                    self.log.error(f"error in cog {filename}, {curr}/{total} | {error}")

                curr += 1  # + 1 for current amount

    def reload_extensions(self):
        curr, total = 1, len(listdir("./cogs")) - 1

        for filename in listdir("./cogs"):
            if filename.endswith(".py"):
                try:  # load cog
                    self.reload_extension(f"cogs.{filename[:-3]}")
                    self.log.info(f"cog {filename} reload, {curr}/{total}")

                except Exception as error:  # something in cog wrong
                    self.log.error(f"error in cog {filename}, {curr}/{total} | {error}")

                curr += 1  # + 1 for current amount


# =============================================================================

instance = None


def get_instance():
    """Singleton getter"""
    global instance
    if instance is None:
        instance = NoirBot()
    return instance
