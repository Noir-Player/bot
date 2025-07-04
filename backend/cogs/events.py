from _logging import get_logger
from disnake.ext import commands
from entities.bot import NoirBot
from entities.node import create_node
from entities.player import NoirPlayer
from services import persiktunes

log = get_logger("events")


class EventsCog(commands.Cog):
    def __init__(self, bot: NoirBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_persiktunes_track_start(
        self, player: NoirPlayer, track: persiktunes.Track
    ):
        await player.edit_controller(player.current.ctx)

        if player.update_controller.is_running():
            player.update_controller.restart()
        else:
            player.update_controller.start()

        if not track.info.isStream:
            try:  # I don't know why it's raising an exception, but it works
                player.update_controller.change_interval(
                    seconds=track.info.length / 1000 / 20
                )
            except:
                pass

        else:
            player.update_controller.stop()

        log.debug(f"{track} started")

    @commands.Cog.listener()
    async def on_persiktunes_track_end(
        self, player: NoirPlayer, track: persiktunes.Track, reason
    ):
        player.update_controller.stop()

        log.debug(f"{track} ended. Reason: {reason}")

        if not player.queue.is_empty and reason in (
            "finished",
            "stopped",
        ):

            try:
                return await player.play(player.queue.get())
            except:
                pass

        elif reason == "replaced":
            return

        await player.queue.clear()

        await player.edit_controller(
            embed=self.bot.embedding.get(
                image="https://noirplayer.su/cdn/ambient.gif",
                color="secondary",
                use_light_color=True,
            ),
        )

    @commands.Cog.listener()
    async def on_ready(self):
        log.info(f"Starting as {self.user} (ID: {self.user.id})")
        log.info("on_ready was called, creating node...")

        await create_node(self.bot)

    @commands.Cog.listener()
    async def on_shard_connect(self, id):
        log.debug(f"Player connected | {id}")


def setup(bot: commands.Bot):
    bot.add_cog(EventsCog(bot))
