import time

import disnake
from assets.emojis import *
from components.embeds import *
from components.modals.playlist import PlaylistInfoModal
from disnake.ext.commands import Paginator
from exceptions import on_view_error
from services.persiktunes import Node
from validators.player import check_player_btn


class QueueButtons(disnake.ui.View):

    def __init__(self, node: Node, message: disnake.Message, embed_queue: "EmbedQueue"):
        self.node = node

        self.embed_queue = embed_queue

        self.message = message

        self.api = node.rest.abstract_search

        super().__init__(timeout=600)

        self.on_error = on_view_error  # type: ignore

        if embed_queue.paginator.pages.__len__() < 2:
            self.children = self.children[2:]

    @disnake.ui.button(
        emoji=PREVIOUS,
        row=0,
    )
    @check_player_btn()
    async def prev(self, button, interaction):
        if self.embed_queue.index > 0:
            self.embed_queue.index -= 1
            return await self.embed_queue.generate_pages(interaction)

    @disnake.ui.button(
        emoji=NEXT,
        row=0,
    )
    @check_player_btn()
    async def next(self, button, interaction):
        if (self.embed_queue.index + 1) < len(self.embed_queue.paginator.pages):
            self.embed_queue.index += 1
            return await self.embed_queue.generate_pages(interaction)

    @disnake.ui.button(
        emoji=REFRESH,
        row=1,
    )
    @check_player_btn()
    async def refresh(self, button, interaction):  # type: ignore
        return await self.embed_queue.generate_pages(interaction)

    @disnake.ui.button(
        emoji=SHUFFLE,
        row=1,
    )
    @check_player_btn()
    async def shuffle(self, button, interaction):
        player = self.node.get_player(interaction.guild_id)
        if not player:
            return
        player.queue.shuffle()

    @disnake.ui.button(
        emoji=AUTOPLAY,
        row=1,
    )
    @check_player_btn()
    async def start_autoplay(self, button, interaction):
        player = self.node.get_player(interaction.guild_id)
        if not player.current:
            return

        if not player.queue.loose_mode:
            await interaction.send(
                embed=PrimaryEmbed(
                    description=f"Autoplay from `{player.current.info.title}` is generating up, wait a bit for tracks 👾",
                ),
                ephemeral=True,
            )
            await player.queue.start_autoplay(player.current)

        else:
            await interaction.send(
                embed=PrimaryEmbed(
                    description=f"Autoplay is disabled 👾",
                ),
                ephemeral=True,
            )

            await player.queue.stop_autoplay()

    @disnake.ui.button(
        emoji=SAVE,
        label="save",
        row=1,
    )
    @check_player_btn(with_defer=False)
    async def save(self, button, interaction):
        player = self.node.get_player(interaction.guild_id)

        if not player.queue.count:
            return

        await interaction.response.send_modal(
            PlaylistInfoModal(
                node=self.node,
                title="Save to library 💫",
                tracks=player.queue.get_queue(),
            )
        )


class EmbedQueue:

    def __init__(self, node: Node):
        self.node = node

        self.message: disnake.Message

        self.index = 0
        self.paginator = Paginator(prefix="```diff\n", max_size=1000)

    async def generate_pages(self, inter):
        self.player = self.node.get_player(inter.guild_id)

        if not self.player:
            return await self.message.delete()

        total = 0

        self.paginator.clear()

        for i, val in enumerate(self.player.queue.get_queue()):

            if val == self.player.current:
                ind = (
                    f"+ {' '*len(str(i))}" if not self.player.queue.loose_mode else "+ "
                )
            else:
                ind = f"{i + 1}" + (". " if not self.player.queue.loose_mode else f"* ")

            self.paginator.add_line(
                f"{ind}{val.info.title} - {val.info.author} ({val.requester.display_name if val.requester else 'secret guest'})"
            )

            total += (val.info.length) / 1000

        total = int(time.time() + total)

        embed = (
            PrimaryEmbed(
                description=(
                    self.paginator.pages[self.index]
                    if self.paginator.pages
                    else "Queue is empty now 👾"
                ),
            )
            .add_field(
                name="Track count",
                value=f"`{self.player.queue.count}`",
                inline=True,
            )
            .add_field(
                name="End time",
                value=f"<t:{total}:R>",
                inline=True,
            )
            .add_field(
                name="Autoplay",
                value=f"`{'yep' if self.player.queue.loose_mode else 'nah'}`",
                inline=True,
            )
            .set_footer(
                text=(
                    f"page {self.index + 1}/{len(self.paginator.pages)}"
                    if len(self.paginator.pages)
                    else ""
                )
            )
        )

        await self.message.edit(
            embed=embed,
            view=self.view,
        )

    @property
    def view(self) -> disnake.ui.View:
        return QueueButtons(node=self.node, message=self.message, embed_queue=self)

    async def send(self, ctx: disnake.Interaction):
        "Use this function with `response.defer()` first"
        self.message = await ctx.original_response()
        await self.generate_pages(ctx)
