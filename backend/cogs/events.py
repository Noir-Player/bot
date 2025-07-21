from _logging import get_logger
from components.embeds import PrimaryEmbed
from disnake.ext import commands
from entities.bot import NoirBot
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
        await player.edit_controller(player.current.ctx)  # type: ignore

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

        if reason in (
            "finished",
            "stopped",
        ):

            if item := player.queue.get():
                return await player.play(item)

        elif reason == "replaced":
            return

        player.queue.clear()

        await player.edit_controller(
            embed=PrimaryEmbed(description="Queue is empty 👾")
        )


def setup(bot: NoirBot):
    bot.add_cog(EventsCog(bot))
