import time

import disnake
from disnake.ext.commands import Paginator

from objects.bot import NoirBot
from services.persiktunes import Node
from validators.player import check_player_btn_decorator


class QueueButtons(disnake.ui.View):

    def __init__(self, node: Node, message: disnake.Message, embed_queue: "EmbedQueue"):
        self.node = node
        self.bot: NoirBot = node.bot

        self.embed_queue = embed_queue

        self.message = message

        self.api = node.rest.abstract_search

        super().__init__(timeout=600)

        for i in range(2, 5):
            self.children.insert(
                i,
                disnake.ui.Button(
                    custom_id=i,
                    row=0,
                    disabled=True,
                ),
            )

        if embed_queue.paginator.pages.__len__() < 2:
            self.children = self.children[5:]

    @disnake.ui.button(
        emoji="<:skip_previous_primary:1239113698623225908>",
        row=0,
    )
    @check_player_btn_decorator()
    async def prev(self, button, interaction):
        await interaction.response.defer()
        if self.embed_queue.index > 0:
            self.embed_queue.index -= 1
            return await self.embed_queue.generate_pages(interaction)

    @disnake.ui.button(
        emoji="<:skip_next_primary:1239113700594679838>",
        row=0,
    )
    @check_player_btn_decorator()
    async def next(self, button, interaction):
        if (self.embed_queue.index + 1) < len(self.embed_queue.paginator.pages):
            self.embed_queue.index += 1
            return await self.embed_queue.generate_pages(interaction)

    @disnake.ui.button(
        emoji="<:refresh_primary:1243850637112774697>",
        row=1,
    )
    @check_player_btn_decorator()
    async def refresh(self, button, interaction):
        return await self.embed_queue.generate_pages(interaction)

    @disnake.ui.button(
        emoji="<:shuffle_primary:1239115175337001071>",
        row=1,
    )
    @check_player_btn_decorator()
    async def shuffle(self, button, interaction):
        player = self.node.get_player(interaction.guild_id)
        if not player:
            return
        await player.queue.shuffle()

    @disnake.ui.button(
        emoji="<:autoplay_primary:1239113693690859564>",
        row=1,
    )
    @check_player_btn_decorator()
    async def start_autoplay(self, button, interaction):
        player = self.node.get_player(interaction.guild_id)
        if not player.current:
            return
        await interaction.send(
            embed=self.bot.embedding.get(
                title="🟣 | Autoplay",
                description=f"Автоплей на основе трека `{player.current.info.title}` запущен, подождите немного...",
            ),
            ephemeral=True,
        )
        await player.queue.start_autoplay(player.current)

    @disnake.ui.button(
        emoji="<:save_primary:1239113692306739210>",
        label="сохранить",
        row=1,
    )
    @check_player_btn_decorator()
    async def save(self, button, interaction):
        player = self.node.get_player(interaction.guild_id)
        if not player.queue.count:
            return
        tracks = [
            track.model_dump(exclude=["ctx", "requester"])
            for track in player.queue.get_queue()
        ]

        from components.ui.modals import PlaylistInfoModal

        await interaction.response.send_modal(
            PlaylistInfoModal(
                node=player.node, title="Сохранить очередь", tracks=tracks
            )
        )


class EmbedQueue:

    def __init__(self, node: Node):
        self.node = node
        self.bot: NoirBot = node.bot

        self.message = None

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

            self.paginator.add_line(ind + val.info.title)

            total += (val.info.length) / 1000

        total = int(time.time() + total)

        await self.message.edit(
            embed=inter.bot.embedding.get(
                {"name": "Всего треков", "value": f"`{self.player.queue.count}`"},
                {"name": "Закончится", "value": f"<t:{total}:R>"},
                {
                    "name": "Автоплей",
                    "value": f"`{'да' if self.player.queue.loose_mode else 'нет'}`",
                },
                title="🟣 | Очередь",
                description=(
                    self.paginator.pages[self.index]
                    if self.paginator.pages
                    else "```diff\n- Пусто!\n```"
                ),
                footer=(
                    f"page {self.index + 1}/{len(self.paginator.pages)}"
                    if len(self.paginator.pages)
                    else None
                ),
                image="https://noirplayer.su/cdn/ambient.gif",
            ),
            view=self.view(),
        )

    def view(self) -> disnake.ui.View:
        """Return view of track (buttons)"""
        return QueueButtons(node=self.node, message=self.message, embed_queue=self)

    async def send(self, ctx: disnake.Interaction, ephemeral: bool = True):
        """Send embed with track info"""
        # await ctx.response.defer(ephemeral=ephemeral)

        self.message = await ctx.original_response()

        await self.generate_pages(ctx)
