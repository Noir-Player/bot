import time

import disnake
from disnake.ext.commands import Paginator

from objects.bot import NoirBot
from services.persiktunes import Node, Playlist, Track, YoutubeMusicSearch
from validators.player import check_player_btn_decorator

from .track import EmbedTrack


class PlaylistButtons(disnake.ui.View):

    def __init__(
        self,
        node: Node,
        message: disnake.Message,
        embed_playlist: "EmbedPlaylist",
        track: Track | None = None,
        local: bool = False,
    ):
        self.node = node
        self.api = YoutubeMusicSearch(node=node)
        self.bot: NoirBot = node.bot

        self.local = local  # TODO: if local playlist, show edit and follow buttons

        self.embed_playlist = embed_playlist

        self.message = message

        self.track = track

        if not track:  # Main page
            self.prev.disabled = True
            self.lyrics.disabled = True
            self.put.disabled = True
            self.start_autoplay.disabled = True

        elif (
            embed_playlist.playlist.tracks.index(track)
            == embed_playlist.playlist.get_length() - 1
        ):
            self.next.disabled = True

        else:
            self.remove_item(self.save)

        super().__init__(timeout=600)

    @disnake.ui.button(
        emoji="<:skip_previous_primary:1239113698623225908>",
        row=0,
    )
    async def prev(self, button, interaction):
        await interaction.response.defer()
        if self.embed_playlist.index > 0:
            self.embed_playlist.index -= 1
            return await self.embed_playlist.generate_pages(interaction)

    @disnake.ui.button(
        emoji="<:skip_next_primary:1239113700594679838>",
        row=0,
    )
    async def next(self, button, interaction):
        await interaction.response.defer()
        if (self.embed_playlist.index) < self.embed_playlist.playlist.get_length():
            self.embed_playlist.index += 1
            return await self.embed_queue.generate_pages(interaction)

    @disnake.ui.button(
        emoji="<:playlist_add_primary:1239115838557126678>",
        row=0,
    )
    @check_player_btn_decorator(with_connection=True)
    async def put(self, button, interaction):
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

        await interaction.send(
            embed=self.bot.embedding.get(
                title="🟣 | Autoplay",
                description='Автоплей на основе трека запущен.\nТеперь очередь будет "сыпаться" и добавлять в себя треки на основе рекомендаций.',
                image=self.track.info.artworkUrl,
            ),
            ephemeral=True,
        )

    @disnake.ui.button(
        emoji="<:lyrics_primary:1239113708203020368>",
        row=0,
    )
    async def lyrics(self, button, interaction):
        await interaction.response.defer(ephemeral=True)
        self.track = await self.api.lyrics(self.track)

        if self.track.lyrics:
            await interaction.send(
                embed=self.bot.embedding.get(
                    author_name=self.track.info.title + " - lyrics",
                    author_icon=self.track.info.artworkUrl,
                    author_url=self.track.info.url,
                    description="```fix\n" + self.track.lyrics + "\n```",
                    footer=(
                        f"Album: {self.track.album.name}" if self.track.album else ""
                    ),
                ),
                ephemeral=True,
            )

    @disnake.ui.button(
        emoji="<:save_primary:1239113692306739210>",
        row=0,
    )
    async def save(self, button, interaction):
        tracks = [
            track.model_dump(exclude=["ctx", "requester"])
            for track in self.player.queue.get_queue()
        ]

        from components.ui.modals import PlaylistInfoModal

        await interaction.response.send_modal(
            PlaylistInfoModal(
                node=self.player.node,
                title="Сохранить плейлист как свой",
                tracks=tracks,
            )
        )


class EmbedPlaylist:

    def __init__(self, node: Node, playlist: Playlist):
        self.node = node
        self.api = YoutubeMusicSearch(node=node)
        self.bot: NoirBot = node.bot

        self.message: disnake.Message = None

        self.playlist = playlist

        self.index = 0

    async def generate_pages(self):
        """"""

        if self.index:
            embed = EmbedTrack(self.playlist.tracks[self.index - 1], self.node).embed()

        else:
            image = (
                self.playlist.thumbnail
                if self.playlist.thumbnail
                else f"https://mir-s3-cdn-cf.behance.net/project_modules/disp/a11a4893658133.5e98adbead405.gif"
            )

            embed = self.bot.embedding.get(
                description=self.playlist.description,
                author_name=self.playlist.info.name,
                author_url=self.playlist.uri,
                image=image,
                color=self.playlist.color,
            )

        await self.message.edit(embed=embed, view=self.view())

    def view(self) -> disnake.ui.View:
        """Return view of track (buttons)"""
        return PlaylistButtons(
            track=self.track, node=self.node, message=self.message, index=self.index - 1
        )

    async def send(self, ctx: disnake.Interaction, ephemeral: bool = True):
        """Send embed with track info"""
        await ctx.response.defer(ephemeral=ephemeral)

        self.message = await ctx.original_response()

        await self.generate_pages(ctx)
