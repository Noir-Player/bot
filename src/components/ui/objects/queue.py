import time

import disnake
from disnake.ext.commands import Paginator

from objects.bot import NoirBot
from services.persiktunes import Node, YoutubeMusicSearch
from validators.player import check_player_btn_decorator


class QueueButtons(disnake.ui.View):

    def __init__(self, node: Node, message: disnake.Message, embed_queue: "EmbedQueue"):
        self.node = node
        self.api = YoutubeMusicSearch(node=node)
        self.bot: NoirBot = node.bot

        self.embed_queue = embed_queue

        self.message = message

        super().__init__(timeout=600)

    @disnake.ui.button(
        emoji="<:skip_previous_primary:1239113698623225908>",
        row=0,
    )
    async def prev(self, button, interaction):
        await interaction.response.defer()
        if self.index > 0:
            self.index -= 1
            return await self.embed_queue.generate_pages(interaction)

    @disnake.ui.button(
        emoji="<:skip_next_primary:1239113700594679838>",
        row=0,
    )
    async def next(self, button, interaction):
        await interaction.response.defer()
        if (self.index + 1) < len(self.pag.pages):
            self.index += 1
            return await self.embed_queue.generate_pages(interaction)

    @disnake.ui.button(
        emoji="<:playlist_add_primary:1239115838557126678>",
        row=0,
    )
    @check_player_btn_decorator(with_connection=True)
    async def add(self, button, interaction):
        player = self.node.get_player(interaction.guild_id)
        await player.queue.put(self.track)
        if not player.current:
            await player.play(player.queue.get())

    @disnake.ui.button(
        emoji="<:autoplay_primary:1239113693690859564>",
        row=0,
    )
    @check_player_btn_decorator(with_connection=True)
    async def start_autoplay(self, button, interaction):
        player = self.node.get_player(interaction.guild_id)
        await player.queue.start_autoplay(self.track)

    @disnake.ui.button(
        emoji="<:lyrics_primary:1239113708203020368>",
        row=0,
    )
    async def lyrics(self, button, interaction):
        self.track = await self.api.lyrics(self.track)

        await interaction.send(
            embed=self.bot.embedding.get(
                author_name=self.track.info.title,
                author_icon=self.track.info.artworkUrl,
                description="```fix\n" + self.track.lyrics + "\n```",
                footer=f"Album: {self.track.album.name}" if self.track.album else "",
                color="info",
            ),
            ephemeral=True,
        )

    @disnake.ui.button(
        emoji="<:save_primary:1239113692306739210>",
        label="сохранить",
        row=0,
        style=disnake.ButtonStyle.gray,
    )
    async def shuffle(self, button, interaction):
        tracks = [
            track.model_dump(exclude=["ctx", "requester"])
            for track in self.player.queue.get_queue()
        ]

        from components.ui.modals import PlaylistInfoModal

        await interaction.response.send_modal(
            PlaylistInfoModal(
                node=self.player.node, title="Сохранить очередь", tracks=tracks
            )
        )


class EmbedQueue:

    def __init__(self, node: Node):
        self.node = node
        self.api = YoutubeMusicSearch(node=node)
        self.bot: NoirBot = node.bot

        self.message = None

        self.index = 0
        self.paginator = Paginator(prefix="```md\n", max_size=1000)

    async def generate_pages(self, inter):

        n = 1

        for val in self.player.queue.get_queue():

            if n - 1 == self.player.queue.find_position(self.player.current):
                ind = f"# {' '*len(str(n))}"
            else:
                ind = f"{n}. "

            self.paginator.add_line(ind + val.info.title)

            n += 1

        total = (
            (
                (
                    sum(
                        i.info.length
                        for i in self.player.queue.get_queue()[
                            self.player.queue.find_position(self.player.current) :
                        ]
                    )
                    - self.player.position
                )
                / 1000
            )
            if not self.player.queue.is_empty
            else 0
        )

        total = int(time.time() + total)

        await self.message.edit(
            embed=inter.bot.embedding.get(
                {"name": "Всего треков", "value": f"`{self.player.queue.count}`"},
                {"name": "Закончится", "value": f"<t:{total}:R>"},
                {"name": "Автоплей", "value": f"`нет`"},
                title="🟣 | Очередь",
                description=self.pag.pages[self.index],
                footer=f"page {self.index + 1}/{len(self.pag.pages)}",
            ),
            view=self.view(await inter.original_response()),
        )

    def view(self) -> disnake.ui.View:
        """Return view of track (buttons)"""
        return QueueButtons(track=self.track, node=self.node, message=self.message)

    async def send(self, ctx: disnake.Interaction, ephemeral: bool = True):
        """Send embed with track info"""
        await ctx.response.defer(ephemeral=ephemeral)

        self.message = await ctx.original_response()

        await self.generate_pages(ctx)
