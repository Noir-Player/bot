import disnake
from components.embeds import *
from services.persiktunes import Node
from services.persiktunes.filters import *
from validators.player import check_player_btn_decorator

from .effects import EmbedEffects


class ContextView(disnake.ui.View):

    def __init__(self, node: Node):
        self.node = node

        super().__init__(timeout=600)

        self.api = node.rest.abstract_search

    @disnake.ui.button(emoji="<:volume_down:1396929533776498739>", row=0)
    @check_player_btn_decorator()
    async def volume_down(self, button, interaction):
        await self.node.get_player(interaction.guild_id).volume_down()

    @disnake.ui.button(emoji="<:volume_up:1396929535911661648>", row=0)
    @check_player_btn_decorator()
    async def volume_up(self, button, interaction):
        await self.node.get_player(interaction.guild_id).volume_up()

    @disnake.ui.button(
        emoji="<:thumb_up:1396929532384247939>",
        row=1,
        disabled=True,
    )
    @check_player_btn_decorator(with_message=True)
    async def add_to_stars(self, button, interaction):
        await interaction.response.defer(ephemeral=True)
        # TODO: write a db models first

    @disnake.ui.button(
        emoji="<:replace_audio:1396929530341622002>",
        row=1,
        style=disnake.ButtonStyle.gray,
    )
    @check_player_btn_decorator(with_message=True)
    async def alternative(self, button, interaction):
        await interaction.response.defer(ephemeral=True)
        # TODO: write an Album object first

    @disnake.ui.button(
        emoji="<:tune:1396929527883501640>",
        row=2,
    )
    @check_player_btn_decorator(with_message=True)
    async def effects_open(self, button, interaction):
        await EmbedEffects(self.node).send(interaction)

    @disnake.ui.button(
        emoji="<:lyrics:1396929525287354410>",
        row=2,
    )
    @check_player_btn_decorator()
    async def lyrics(self, button, interaction):
        player = self.node.get_player(interaction.guild_id)
        if not player.current:
            return

        track = await self.api.lyrics(player.current)

        if not track.lyrics:
            return

        embed = SecondaryEmbed(
            title=track.info.title,
            description="```fix\n" + track.lyrics + "\n```",
        ).set_author(name=track.info.author, icon_url=track.info.artworkUrl)

        if track.album:
            embed.set_footer(text=f"Album: {track.album.name}")

        await interaction.send(
            embed=embed,
            ephemeral=True,
        )


class EmbedContext:

    def __init__(self, node: Node):
        self.node = node

    @property
    def view(self) -> disnake.ui.View:
        return ContextView(node=self.node)

    async def send(self, ctx: disnake.Interaction):
        "Use this function with `response.defer()` first"
        await ctx.edit_original_response(view=self.view)
