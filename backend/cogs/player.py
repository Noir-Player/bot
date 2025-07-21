import datetime

import disnake
from components.embeds import *
from components.views.context import EmbedContext
from components.views.effects import EmbedEffects
from components.views.soundpad import state
from disnake.ext import commands
from entities.bot import NoirBot
from entities.node import Node
from entities.node import get_instance as get_node
from entities.player import NoirPlayer
from exceptions import *
from validators.player import check_player_decorator


class PlayerCog(commands.Cog):
    def __init__(self, bot: NoirBot):
        self.bot = bot
        self.node: Node = get_node()

    def _calculate_seconds(self, time_code):
        if len(time_code) == 5:
            time_format = "%M:%S"
        elif len(time_code) == 8:
            time_format = "%H:%M:%S"
        else:
            return None

        try:
            time_obj = datetime.strptime(time_code, time_format)
            seconds = (time_obj - datetime(1900, 1, 1)).total_seconds()
            return seconds
        except BaseException:
            return None

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Player

    # TODO: Database

    @commands.slash_command(name="player")
    @commands.contexts(guild=True)
    async def _player(self, _):
        pass

    @check_player_decorator(with_defer=False)
    @_player.sub_command(description="✨✨ | Current track")
    async def now(
        self,
        inter: disnake.ApplicationCommandInteraction,
        hidden: int = commands.Param(
            default=0,
            description="Must I show it to you only?",
            choices=[
                disnake.OptionChoice(name="Yes", value=1),
                disnake.OptionChoice(name="No", value=0),
            ],
        ),
    ):
        await inter.response.defer(ephemeral=bool(hidden))
        player: NoirPlayer = self.node.get_player(inter.guild_id)  # type: ignore
        await inter.send(embed=state(player), ephemeral=True)

    @check_player_decorator(with_defer=False)
    @_player.sub_command(description="✨ | Extra menu")
    async def menu(
        self,
        inter: disnake.ApplicationCommandInteraction,
        hidden: int = commands.Param(
            default=0,
            description="Must I show it to you only?",
            choices=[
                disnake.OptionChoice(name="Yes", value=1),
                disnake.OptionChoice(name="No", value=0),
            ],
        ),
    ):
        await inter.response.defer(ephemeral=bool(hidden))
        await EmbedContext(self.node).send(inter)

    @check_player_decorator()
    @_player.sub_command(description="✨ | Set the volume")
    async def volume(
        self,
        inter: disnake.ApplicationCommandInteraction,
        volume: int = commands.Param(
            description="Percentage", min_value=0, max_value=500
        ),
    ):
        player: NoirPlayer = self.node.get_player(inter.guild_id)  # type: ignore
        await player.set_volume(volume)
        await inter.delete_original_message()

    @check_player_decorator()
    @_player.sub_command(description="✨ | Pause or resume")
    async def pause(
        self,
        inter: disnake.ApplicationCommandInteraction,
    ):
        player: NoirPlayer = self.node.get_player(inter.guild_id)  # type: ignore
        if player.is_playing or player.is_paused:
            await player.set_pause()

        await inter.delete_original_message()

    @check_player_decorator()
    @_player.sub_command(description="✨ | Seek to timecode")
    async def seek(
        self,
        inter: disnake.ApplicationCommandInteraction,
        timecode: str = commands.Param(
            description="Timecode mm:ss or hh:mm:ss", min_length=5, max_length=8
        ),
    ):
        player: NoirPlayer = self.node.get_player(inter.guild_id)  # type: ignore
        mseconnds = self._calculate_seconds(timecode)

        if mseconnds:
            await player.seek(int(mseconnds * 1000))
            await player.update_controller_once()
        await inter.delete_original_message()

    @check_player_decorator()
    @_player.sub_command(description="✨ | Rewind in seconds")
    async def rewind(
        self,
        inter: disnake.ApplicationCommandInteraction,
        seconds: int = commands.Param(description="Count of seconds, can be negative"),
    ):
        player: NoirPlayer = self.node.get_player(inter.guild_id)  # type: ignore
        await player.seek(int(player.position + float(seconds * 1000)))
        await player.update_controller_once()
        await inter.delete_original_message()

    @check_player_decorator()
    @_player.sub_command(description="✨ | Destroy player")
    async def stop(
        self,
        inter: disnake.ApplicationCommandInteraction,
    ):
        try:
            await inter.guild.voice_client.disconnect(force=True)  # type: ignore (decorator has warranty about voice client)
        except BaseException:
            pass

        await inter.delete_original_message()

    @check_player_decorator(with_connection=True)
    @_player.sub_command(description="✨ | Connect Noir to voice channel")
    async def join(self, ctx):
        await ctx.delete_original_message()

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Effects

    @_player.sub_command_group()
    async def effects(self, _):
        pass

    @check_player_decorator()
    @effects.sub_command(description="⭐⭐ | Effects menu")
    async def open(
        self,
        inter: disnake.ApplicationCommandInteraction,
        hidden: int = commands.Param(
            default=0,
            description="Must I show it to you only?",
            choices=[
                disnake.OptionChoice(name="Yes", value=1),
                disnake.OptionChoice(name="No", value=0),
            ],
        ),
    ):
        await inter.response.defer(ephemeral=bool(hidden))
        await EmbedEffects(self.node).send(inter)

    @check_player_decorator()
    @effects.sub_command(description="⭐ | Remove all effects")
    async def reset(
        self,
        inter: disnake.ApplicationCommandInteraction,
    ):
        player: NoirPlayer = self.node.get_player(inter.guild_id)  # type: ignore
        await player.reset_filters()
        await inter.delete_original_message()

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Контроллер

    @_player.sub_command_group()
    async def controller(self, _):
        pass

    @check_player_decorator()
    @controller.sub_command(description="⭐⭐ | Where is the controller?")
    async def where(
        self,
        inter: disnake.ApplicationCommandInteraction,
    ):
        player: NoirPlayer = self.node.get_player(inter.guild_id)  # type: ignore

        try:
            return await inter.send(
                embed=PrimaryEmbed(
                    title="✨ | Jump to controller", url=player.controller.jump_url  # type: ignore
                ),
                ephemeral=True,
            )
        except BaseException:
            return await inter.send(
                embed=WarningEmbed(
                    title="I can't find the controller",
                    description="Try create one with any `/play` or `/embed resend` command ✨",
                ),
                ephemeral=True,
            )

    @check_player_decorator()
    @controller.sub_command(description="⭐ | Try resend controller")
    async def resend(
        self,
        inter: disnake.ApplicationCommandInteraction,
    ):
        player: NoirPlayer = self.node.get_player(inter.guild_id)  # type: ignore

        if player:
            await player.update_controller_once(True, inter)
        else:
            return await inter.send(
                embed=WarningEmbed(
                    title="You must play a track first",
                    description="Try create player with any `/play` command ✨",
                ),
                ephemeral=True,
            )


def setup(bot: NoirBot):
    bot.add_cog(PlayerCog(bot))
