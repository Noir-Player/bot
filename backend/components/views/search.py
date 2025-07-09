# TODO Idk what is it and how it works

from typing import List, Union

import disnake
from entities.bot import NoirBot
from services.persiktunes import Album, Artist, Node, Playlist, Track
from validators.player import check_player_btn_decorator

from .playlist import EmbedPlaylist
from .track import EmbedTrack


class SearchView(disnake.ui.View):

    def __init__(
        self,
        results: List[Union[Track, Playlist, Album, Artist]],
        node: Node,
        message: disnake.Message,
    ):
        self.results = results
        self.node = node
        self.bot: NoirBot = node.bot

        self.message = message

        self.init_select()

        super().__init__(timeout=600)

        self.api = node.rest.abstract_search

    def init_select(self):

        for i, result in enumerate(self.results):
            if isinstance(result, Playlist, Album):
                self.select.append_option(
                    disnake.SelectOption(
                        label=result.title,
                        description=result.description,
                        emoji="<:queue_music_primary:1239113703824293979>",
                        value=str(i),
                    )
                )

            elif isinstance(result, Track):
                self.select.append_option(
                    disnake.SelectOption(
                        label=result.title,
                        description=result.info.author,
                        emoji="<:music_note_primary:1242559698759319593>",
                        value=str(i),
                    )
                )

    @disnake.ui.select(placeholder="Выберите результат ...", row=0)
    async def select(self, select, interaction):
        result = self.results[int(select.values[0])]

        if isinstance(result, Playlist, Album):
            await EmbedPlaylist(self.node, result).send(interaction)

        elif isinstance(result, Track):
            await EmbedTrack(result, self.node, self.message).send(interaction)

    @disnake.ui.button(
        emoji="<:autoplay_primary:1239113693690859564>",
        row=1,
    )
    @check_player_btn_decorator(with_connection=True)
    async def start_autoplay(self, button, interaction):
        player = self.node.get_player(interaction.guild_id)
        await player.queue.start_autoplay(self.results[0])

    @disnake.ui.button(
        emoji="<:playlist_add_primary:1239115838557126678>",
        row=1,
    )
    @check_player_btn_decorator(with_connection=True)
    async def add(self, button, interaction):
        player = self.node.get_player(interaction.guild_id)
        await player.queue.put(self.results[0])
        if not player.current:
            await player.play(player.queue.get())

    @disnake.ui.button(
        emoji="<:music_note_primary:1242559698759319593>",
        row=1,
        disabled=True,
    )
    @check_player_btn_decorator(with_connection=True)
    async def research_tracks(self, button, interaction):
        pass

    @disnake.ui.button(
        emoji="<:music_note_primary:1242559698759319593>",
        row=1,
        disabled=True,
    )
    @check_player_btn_decorator(with_connection=True)
    async def research_playlists(self, button, interaction):
        pass

    @disnake.ui.button(
        emoji="<:artist_primary:1242559701770702920>",
        row=1,
        disabled=True,
    )
    @check_player_btn_decorator(with_connection=True)
    async def research_artists(self, button, interaction):
        pass

    async def on_timeout(self):
        pass


class EmbedSearch:

    def __init__(self, track: Track, node: Node):
        self.track = track
        self.node = node
        self.bot: NoirBot = node.bot

    def embed(self) -> disnake.Embed:
        """Return embed with track info"""

    def view(self, message: disnake.Message) -> disnake.ui.View:
        return SearchView(track=self.track, node=self.node, message=message)

    async def send(self, ctx: disnake.Interaction):
        "Use this function with `response.defer()` first"
        await ctx.edit_original_response(embed=self.embed())

        message = await ctx.original_response()

        view = self.view(message)

        await message.edit(view=view)
