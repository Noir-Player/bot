import disnake
from components.embeds import *
from entities.bot import NoirBot
from services.persiktunes import Node
from services.persiktunes.filters import *
from validators.player import check_player_btn_decorator

from .effects import EmbedEffects


class ContextView(disnake.ui.View):

    def __init__(self, node: Node):
        self.node = node
        self.bot: NoirBot = node.bot

        super().__init__(timeout=600)

        self.api = node.rest.abstract_search

    @disnake.ui.button(emoji="<:volume_down_primary:1239113694856876076>", row=0)
    @check_player_btn_decorator()
    async def volume_down(self, button, interaction):
        await self.node.get_player(interaction.guild_id).volume_down()

    @disnake.ui.button(emoji="<:volume_up_primary:1239113696337199165>", row=0)
    @check_player_btn_decorator()
    async def volume_up(self, button, interaction):
        await self.node.get_player(interaction.guild_id).volume_up()

    @disnake.ui.button(
        emoji="<:bookmark_primary:1242557997624983592>",
        row=1,
        disabled=True,
    )
    @check_player_btn_decorator(with_message=True)
    async def add_to_stars(self, button, interaction):
        await interaction.response.defer(ephemeral=True)
        # TODO: write a db models first

    @disnake.ui.button(
        emoji="<:alt_route_primary:1239113857461387264>",
        row=1,
        style=disnake.ButtonStyle.gray,
    )
    @check_player_btn_decorator(with_message=True)
    async def alternative(self, button, interaction):
        await interaction.response.defer(ephemeral=True)
        # TODO: write an Album object first

    @disnake.ui.button(
        emoji="<:equalizer_primary:1239113717656977439>",
        row=2,
    )
    @check_player_btn_decorator(with_message=True)
    async def effects_open(self, button, interaction):
        await EmbedEffects(self.node).send(interaction)

    @disnake.ui.button(
        emoji="<:lyrics_primary:1239113708203020368>",
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
        self.bot: NoirBot = node.bot

    @property
    def view(self) -> disnake.ui.View:
        return ContextView(node=self.node)

    async def send(self, ctx: disnake.Interaction):
        "Use this function with `response.defer()` first"
        await ctx.edit_original_response(view=self.view)
