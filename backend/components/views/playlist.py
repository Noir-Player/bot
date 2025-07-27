import disnake
from assets.emojis import *
from assets.fallbacks import NO_COVER_URL
from components.embeds import BaseEmbed, PrimaryEmbed, SecondaryEmbed
from exceptions import on_view_error
from services.persiktunes import Album, Node, Playlist, Track
from validators.player import check_player

from .track import EmbedTrack


class PlaylistButtons(disnake.ui.View):

    def __init__(
        self,
        node: Node,
        embed_playlist: "EmbedPlaylist",
        message: disnake.Message | None = None,
        track: Track | None = None,
        local: bool = False,
    ):
        self.node = node
        self.api = node.rest.abstract_search

        self.local = local  # TODO: if local playlist, show edit and follow buttons

        self.embed_playlist = embed_playlist

        self.message = message

        self.track = track

        self.on_error = on_view_error  # type: ignore

        super().__init__(timeout=600)

        if not track:  # Main page
            self.prev.disabled = True
            self.lyrics.disabled = True
            self.put.disabled = True
            self.start_autoplay.disabled = True

        elif (
            embed_playlist.playlist.tracks.index(track)
            == embed_playlist.playlist.length - 1
        ):
            self.next.disabled = True

        else:
            self.remove_item(self.save)

    @disnake.ui.button(
        emoji=PREVIOUS,
        row=0,
    )
    async def prev(self, button, interaction):
        await interaction.response.defer()
        if self.embed_playlist.index > 0:
            self.embed_playlist.index -= 1
            return await self.embed_playlist.generate_pages()

    @disnake.ui.button(
        emoji=NEXT,
        row=0,
    )
    async def next(self, button, interaction):
        await interaction.response.defer()
        if (self.embed_playlist.index) < self.embed_playlist.playlist.length:
            self.embed_playlist.index += 1
            return await self.embed_playlist.generate_pages()

    @disnake.ui.button(
        emoji=ADD,
        row=0,
    )
    @check_player(with_connection=True)
    async def put(self, button, interaction):
        player = self.node.get_player(interaction.guild_id)
        await player.queue.put(self.track)  # type: ignore
        if not player.current:  # type: ignore
            await player.play(player.queue.get())  # type: ignore

    @disnake.ui.button(
        emoji=AUTOPLAY,
        row=0,
    )
    @check_player(with_connection=True)
    async def start_autoplay(self, button, interaction):
        player = self.node.get_player(interaction.guild_id)
        await player.queue.start_autoplay(self.track)  # type: ignore

        await interaction.send(
            embed=PrimaryEmbed(
                description="Autoplay started 👾\n Queue is on loose mode now"
            ).set_author(
                name=self.track.info.title, icon_url=self.track.info.artworkUrl  # type: ignore
            ),
            ephemeral=True,
        )

    @disnake.ui.button(
        emoji=LYRICS,
        row=0,
    )
    async def lyrics(self, button, interaction):
        await interaction.response.defer(ephemeral=True)

        if not self.track:
            return

        self.track = await self.api.lyrics(self.track) or self.track

        if isinstance(self.track.lyrics, str):
            await interaction.send(
                embed=SecondaryEmbed(
                    description="```fix\n" + self.track.lyrics + "\n```"
                )
                .set_author(
                    name=self.track.info.title,
                    url=self.track.info.uri,
                    icon_url=self.track.info.artworkUrl,
                )
                .set_footer(
                    text=f"Album: {self.track.album.name}" if self.track.album else ""
                ),
                ephemeral=True,
            )

    @disnake.ui.button(
        emoji=SAVE,
        row=1,
    )
    async def save(self, button, interaction):
        player = self.node.get_player(interaction.guild_id)  # type: ignore

        if not player.queue.count:  # type: ignore
            return

        # TODO: save to library

        from components.modals.playlist import PlaylistInfoModal

        await interaction.response.send_modal(
            PlaylistInfoModal(
                node=self.node,
                title="Save to library 💫",
                tracks=player.queue.get_queue(),  # type: ignore
            )
        )


class EmbedPlaylist:

    def __init__(self, node: Node, playlist: Playlist | Album):
        self.node = node
        self.api = node.rest.abstract_search

        self.message: disnake.Message | None = None

        self.playlist = playlist

        self.index = 0

    async def generate_pages(self):
        """"""

        if self.index:
            embed = EmbedTrack(self.playlist.tracks[self.index - 1], self.node).embed()

        else:
            image = self.playlist.thumbnail or NO_COVER_URL

            embed = (
                BaseEmbed(
                    description=self.playlist.description, colour=self.playlist.color
                )
                .set_author(name=self.playlist.info.name, url=self.playlist.uri)
                .set_image(image)
            )

        if self.message:
            await self.message.edit(
                embed=embed,
                view=self.view(),
            )

    def view(self) -> disnake.ui.View:
        """Return view of track (buttons)"""
        return PlaylistButtons(
            track=self.playlist.tracks[self.index - 1] if self.index else None,
            node=self.node,
            message=self.message,
            embed_playlist=self,
        )

    async def send(self, ctx: disnake.Interaction):
        """You can use this function with `response.defer()` first"""
        self.message = await ctx.original_response()

        await self.generate_pages()
