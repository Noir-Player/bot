import pomice
from disnake.ext import commands
from entities.bot import NoirBot
from entities.player import NoirPlayer


class EventsCog(commands.Cog):
    def __init__(self, bot: NoirBot):
        self.bot = bot

    # -------------------------------------------------------------------------------------------------------------------------------------

    # Lavalink events

    @commands.Cog.listener()
    async def on_pomice_track_start(self, player: NoirPlayer, track: pomice.Track):
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

    """Если саундбара нет, его измененение не имеет смысла"""

    """Прослушивание окончания трека"""

    @commands.Cog.listener()
    async def on_pomice_track_end(
        self, player: NoirPlayer, track: pomice.Track, reason
    ):
        player.update_controller.stop()  # останавливаем обновление плеера

        self.bot._log.debug(f"{track} ended. Reason: {reason}")

        if not player.queue.is_empty and reason in (
            "finished",
            "stopped",
        ):  # если трек завершился самостоятельно или использовано skip

            try:
                return await player.play(player.queue.get())
            except:
                pass

        elif reason == "replaced":  # если трек был заменен
            return

        await player.queue.clear()

        await player.edit_controller(
            embed=self.bot.embedding.get(
                image="https://noirplayer.su/cdn/ambient.gif",
                color="secondary",
                use_light_color=True,
            ),
        )

    # -------------------------------------------------------------------------------------------------------------------------------------
    # VOICE_STATE_UPDATE ИВЕНТ NOTE: перенесен в fetcher.py


def setup(bot: commands.Bot):
    bot.add_cog(EventsCog(bot))
