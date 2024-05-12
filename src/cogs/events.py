import asyncio

from disnake.ext import commands

import services.persiktunes as persik
from objects.bot import NoirBot
from objects.player import NoirPlayer


class Events(commands.Cog):
    def __init__(self, bot: NoirBot):
        self.bot = bot
        self.pool = bot.pool

        # -------------------------------------------------------------------------------------------------------------------------------------

    # ИВЕНТЫ ЛАВАЛИНКА

    @commands.Cog.listener()
    async def on_persik_track_start(self, player: NoirPlayer, track: persik.Track):
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
    async def on_persik_track_end(
        self, player: NoirPlayer, track: persik.Track, reason
    ):
        player.update_controller.stop()  # останавливаем обновление плеера

        self.bot._log.debug(f"{track} ended. Reason: {reason}")

        if not player.queue.is_empty and reason in (
            "finished",
            "stopped",
        ):  # если трек завершился самостоятельно или использовано skip
            sound = player.queue.get()  # получаем трек
            if sound:  # если очередь не пуста
                return await player.play(sound)

        elif reason == "replaced":  # если трек был заменен
            return

        await player.queue.clear()

        try:
            await player.controller.delete(5)
        except:
            pass

    # -------------------------------------------------------------------------------------------------------------------------------------
    # VOICE_STATE_UPDATE ИВЕНТ NOTE: перенесен в fetcher.py


def setup(bot: commands.Bot):
    bot.add_cog(Events(bot))
