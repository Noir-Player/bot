import disnake

from objects.bot import NoirBot
from services.persiktunes import Node, YoutubeMusicSearch
from services.persiktunes.filters import *
from validators.player import check_player_btn_decorator


class ContextView(disnake.ui.View):

    def __init__(self, node: Node):
        self.node = node
        self.bot: NoirBot = node.bot

        self.api = YoutubeMusicSearch(node=node)

        super().__init__(timeout=600)

    @disnake.ui.button(emoji="<:volume_down_primary:1239113694856876076>", row=0)
    @check_player_btn_decorator()
    async def volume_down(self, button, interaction):
        await self.node.get_player(interaction.guild_id).volume_down()

    @disnake.ui.button(emoji="<:volume_up_primary:1239113696337199165>", row=0)
    @check_player_btn_decorator()
    async def volume_up(self, button, interaction):
        await self.node.get_player(interaction.guild_id).volume_up()

    @disnake.ui.button(
        emoji="<:autoplay_primary:1239113693690859564>",
        row=0,
    )
    @check_player_btn_decorator()
    async def start_autoplay(self, button, interaction):
        player = self.node.get_player(interaction.guild_id)
        if player.current:
            await player.queue.start_autoplay(self.track)

    @disnake.ui.button(
        emoji="<:bookmark_primary:1242557997624983592>",
        row=1,
    )
    @check_player_btn_decorator(with_message=True)
    async def add_to_stars(self, button, interaction):
        await interaction.response.defer(ephemeral=True)
        # NOTE: write a db models first

    @disnake.ui.button(
        emoji="<:alt_route_primary:1239113857461387264>",
        label="найти альтернативы",
        row=1,
        style=disnake.ButtonStyle.gray,
    )
    @check_player_btn_decorator(with_message=True)
    async def alternative(self, button, interaction):
        await interaction.response.defer(ephemeral=True)
        # NOTE: write an Album object first


class EmbedContext:

    def __init__(self, node: Node):
        self.node = node
        self.bot: NoirBot = node.bot

    def view(self) -> disnake.ui.View:
        """Return view (buttons)"""
        return ContextView(node=self.node)

    async def send(self, ctx: disnake.Interaction, ephemeral: bool = True):
        """Send effects"""
        await ctx.response.send_message(ephemeral=ephemeral, view=self.view())
