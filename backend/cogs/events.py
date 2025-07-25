from _logging import get_logger
from components.embeds import PrimaryEmbed
from disnake.ext import commands
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

        log.debug(f"{track} started with context {track.ctx} | {player.current.ctx}")

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
    async def on_persik_track_end(
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
            embed=PrimaryEmbed(description="Queue is empty 👾").set_image(
                url="https://i.pinimg.com/736x/4f/91/b0/4f91b000e3f40bcc52e318c2f0b1a3eb.jpg"
            )
        )

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        player = self.node.get_player(member.guild.id)

        if not player:
            return

        if member.id == self.bot.user.id and before.channel and not after.channel:
            await player.destroy()


def setup(bot: NoirBot):
    bot.add_cog(EventsCog(bot))
