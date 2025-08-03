from _logging import get_logger
from disnake.ext import commands, tasks
from entities.bot import NoirBot
from entities.node import get_instance as get_node
from entities.player import NoirPlayer
from exceptions import on_error
from services import persiktunes

log = get_logger("events")


class EventsCog(commands.Cog):
    def __init__(self, bot: NoirBot):
        self.bot = bot
        self.node = get_node()

        self.bot.add_listener(on_error, "on_slash_command_error")
        self.bot.add_listener(on_error, "on_user_command_error")
        self.bot.add_listener(on_error, "on_message_command_error")

    @commands.Cog.listener()
    async def on_persik_track_start(self, player: NoirPlayer, track: persiktunes.Track):
        await player.edit_controller(player.current.ctx)  # type: ignore

        log.debug(f"{track} started with context {track.ctx} | {player.current.ctx}")  # type: ignore

        if player.update_controller.is_running():
            player.update_controller.restart()
        else:
            player.update_controller.start()

        if not track.info.isStream:
            try:  # I don't know why it's raising an exception, but it works
                player.update_controller.change_interval(
                    seconds=track.info.length / 1000 / 40
                )
            except:
                pass

        else:
            player.update_controller.stop()

        log.debug(f"{track} started")

        self.autoplay_task.cancel()

    @commands.Cog.listener()
    async def on_persik_track_end(
        self, player: NoirPlayer, track: persiktunes.Track, reason: persiktunes.Reason
    ):
        player.update_controller.stop()

        log.debug(f"{track} ended. Reason: {reason.value}")

        if reason.value in ("finished", "stopped"):

            if item := player.queue.get():
                return await player.play(item)

        elif reason.value == "replaced":
            return

        player.queue.clear()

        await player.edit_controller()

        self.autoplay_task.start(player)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        player = self.node.get_player(member.guild.id)

        if not player:
            return

        if (
            member.id == self.bot.user.id and before.channel and not after.channel
        ):  # if bot was kicked
            return await player.destroy()

        if len(player.channel.members) < 2:  # handle if bot single
            self.destroy_task.start(player)
        else:
            self.destroy_task.cancel()  # cancel task

    @tasks.loop(seconds=30)
    async def destroy_task(self, player: NoirPlayer):
        if player.is_connected:
            await player.destroy()

    @tasks.loop(minutes=1)
    async def autoplay_task(self, player: NoirPlayer):
        if player.is_connected:
            # await player.autoplay()
            pass  # TODO


def setup(bot: NoirBot):
    bot.add_cog(EventsCog(bot))
