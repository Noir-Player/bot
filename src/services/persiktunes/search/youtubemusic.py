from typing import Any, Dict, List

import ytmusicapi

from services.persiktunes.models import Album, Browse, Mood

from ..models import LavalinkPlaylistInfo, LavalinkTrackInfo, Playlist, Track
from .template import BaseSearch


class YoutubeMusicSearch(BaseSearch):
    """
    Youtube Music search abstract class.

    You can use mathods without `Node`, just pass context in `kwargs` and go:

    ```py
    from persiktunes import YoutubeMusicSearch
    ...
    search = YoutubeMusicSearch(node = node)
    ...
    @commands.slash_command(description="Play song")
    asyng def play(self, ctx, query: str):
        songs = await search.search_songs(query, ctx=ctx, requester=ctx.author)
        ...
        await player.play(songs[0])
    ```
    """

    def __init__(self, node: Any, **kwargs) -> None:
        """Pass a `Node` instance and get started.\nYou can pass any additional kwarg: `language`"""
        self.client = ytmusicapi.YTMusic(language=kwargs.get("language", "ru"))
        self.node = node

    async def song(self, id: str, **kwargs) -> Track | None:
        raw = self.client.get_song(id)

        if not raw:
            return None

        raw = raw["videoDetails"]

        info = LavalinkTrackInfo(
            identifier=raw["videoId"],
            isSeekable=True,
            author=",".join([artist["name"] for artist in raw["artists"]]),
            length=int(raw["lengthSeconds"] * 1000),
            isStream=False,
            position=0,
            title=raw["title"],
            uri=f"https://music.youtube.com/watch?v={raw['videoId']}",
            artworkUrl=raw["thumbnails"][0]["url"].split("=")[0],
            sourceName="youtube",
        )

        track = Track(
            encoded=(
                await self.node.rest.send(
                    "GET", f"loadtracks?identifier={raw['videoId']}"
                )
            )["data"]["encoded"],
            info=info,
        )

        return self.node.patch_context(data=track, **kwargs)

    async def album(self, id: str, **kwargs) -> Album | None:
        raw = self.client.get_album(id)

        if not raw:
            return None

        tracks = []

        for rawtrack in raw["tracks"]:

            info = LavalinkTrackInfo(
                identifier=rawtrack["videoId"],
                isSeekable=True,
                author=",".join([artist["name"] for artist in rawtrack["artists"]]),
                length=rawtrack["length"],
                isStream=False,
                position=0,
                title=rawtrack["title"],
                uri=f"https://music.youtube.com/watch?v={rawtrack['videoId']}",
                artworkUrl=(
                    rawtrack["thumbnails"][0]["url"].split("=")[0]
                    if rawtrack["thumbnails"]
                    else None
                ),
                sourceName="youtube",
            )

            tracks.append(
                Track(
                    encoded=(
                        await self.node.rest.send(
                            "GET", f"loadtracks?identifier={rawtrack['videoId']}"
                        )
                    )["data"]["encoded"],
                    info=info,
                )
            )

        info = LavalinkPlaylistInfo(name=raw["title"], selectedTrack=0)

        album = Album(
            info=info,
            tracks=tracks,
            description=raw.get("description"),
            uri=f"https://music.youtube.com/playlist?list={raw['audioPlaylistId']}",
        )

        return self.node.patch_context(data=album, **kwargs)

    async def playlist(self, id: str, **kwargs) -> Playlist | None:
        raw = self.client.get_playlist(id, limit=500)

        if not raw:
            return None

        tracks = []

        for rawtrack in raw["tracks"]:

            info = LavalinkTrackInfo(
                identifier=rawtrack["videoId"],
                isSeekable=True,
                author=",".join([artist["name"] for artist in rawtrack["artists"]]),
                length=rawtrack["length"],
                isStream=False,
                position=0,
                title=rawtrack["title"],
                uri=f"https://music.youtube.com/watch?v={rawtrack['videoId']}",
                artworkUrl=(
                    rawtrack["thumbnails"][0]["url"].split("=")[0]
                    if rawtrack["thumbnails"]
                    else None
                ),
                sourceName="youtube",
            )

            tracks.append(
                Track(
                    encoded=(
                        await self.node.rest.send(
                            "GET", f"loadtracks?identifier={rawtrack['videoId']}"
                        )
                    )["data"]["encoded"],
                    info=info,
                )
            )

        info = LavalinkPlaylistInfo(name=raw["title"], selectedTrack=0)

        playlist = Playlist(
            info=info,
            tracks=tracks,
            description=raw.get("description"),
            uri=f"https://music.youtube.com/playlist?list={raw['audioPlaylistId']}",
        )

        return self.node.patch_context(data=playlist, **kwargs)

    async def moods(self, **kwargs) -> List[Mood]:
        raw = self.client.get_mood_categories()

        moods = []

        for name, rawmoods in raw.items():
            for mood in rawmoods:
                moods.append(Mood(title=mood["title"], params=mood["params"]))

        return moods

    async def get_mood_playlists(self, mood: Mood, **kwargs) -> List[Playlist]:
        raw = self.client.get_mood_playlists(mood.params)

        playlists = []

        for rawplaylist in raw:
            playlist = self.playlist(rawplaylist["playlistId"])
            playlists.append(self.node.patch_context(data=playlist, **kwargs))

        return playlists

    async def search_songs(self, query: str, **kwargs) -> List[Track] | None:
        raw = self.client.search(query, filter="songs")

        if not raw:
            return None

        tracks = []

        for rawresult in raw:
            song = self.song(rawresult["videoId"])
            tracks.append(self.node.patch_context(data=song, **kwargs))

        return tracks

    async def search_albums(self, query: str, **kwargs) -> List[Album] | None:
        raw = self.client.search(query, filter="albums")

        if not raw:
            return None

        albums = []

        for rawresult in raw:
            album = self.album(rawresult["browseId"])
            albums.append(self.node.patch_context(data=album, **kwargs))

        return albums

    async def search_playlists(self, query: str, **kwargs) -> List[Playlist] | None:
        raw = self.client.search(query, filter="playlists")

        if not raw:
            return None

        playlists = []

        for rawresult in raw:
            playlist = self.playlist(rawresult["browseId"])
            playlists.append(self.node.patch_context(data=playlist, **kwargs))

        return playlists

    async def relayted(self, song: Track, **kwargs) -> List[Track]:
        raw = self.client.get_watch_playlist(song.info.identifier, limit=1)

        relayted = self.client.get_song_related(raw["playlistId"])

        tracks = []

        for rawtrack in relayted["tracks"]:
            track = self.song(rawtrack["videoId"])
            tracks.append(self.node.patch_context(data=track, **kwargs))

        return tracks

    async def lyrics(self, song: Track, **kwargs) -> Track | None:
        raw = self.client.get_watch_playlist(song.info.identifier, limit=1)

        if not raw.get("lyrics"):
            return

        lyrics = self.client.get_song_lyrics(raw["lyrics"]).get("lyrics")

        track = song.model_copy(update={"lyrics": lyrics})

        track = self.node.patch_context(data=track, **kwargs)

        return track

    # async def complete_search(self, query: str) -> List[Dict[str, str]]:
    #     """Return a list of search results."""
    #     return self.client.search(query)

    # def _patch_tracks(self, patch: dict, playlist: Any) -> List[Track]:
    #     patched_tracks = []

    #     i = 0

    #     for track in playlist.tracks:
    #         selected_track = patch["tracks"][i]
    #         i += 1

    #         self.node.bot.log.debug(f"selected_track: {selected_track}")

    #         info = track.info.model_copy(
    #             update={
    #                 "artworkUrl": (
    #                     selected_track["thumbnails"][0]["url"].split("=")[0]
    #                     if selected_track.get("thumbnails")
    #                     else (
    #                         patch["thumbnails"][0]["url"].split("=")[0]
    #                         if patch.get("thumbnails")
    #                         else None
    #                     )
    #                 )
    #             }
    #         )

    #         patched_tracks.append(track.model_copy(update={"info": info}))

    #     return patched_tracks

    # async def search(
    #     self, query: str, filter: str = None, only_top: bool = False, **kwargs
    # ) -> LavaSearchLoadingResponse | Union[Track, Playlist]:
    #     response = self.client.search(query, filter)

    #     tracks = []
    #     playlists = []
    #     albums = []
    #     artists = []

    #     for object in response:
    #         self.node.bot.log.debug(f"object: {object}")

    #         if object.get("resultType") in ("video", "song"):
    #             track: Track = (
    #                 await self.node.rest.search(
    #                     query=f"https://music.youtube.com/watch?v={object.get('videoId')}"
    #                 )
    #             ).data

    #             info = track.info.model_copy(
    #                 update={
    #                     "artworkUrl": object.get("thumbnails")[0]["url"].split("=")[0]
    #                 }
    #             )

    #             track = track.model_copy(update={"info": info})

    #             if only_top:
    #                 return track

    #             tracks.append(track)

    #         elif object.get("resultType") == "playlist":
    #             patch = self.client.get_playlist(object.get("browseId"), 700)

    #             playlist: Playlist = (
    #                 await self.node.rest.search(
    #                     query=f"https://music.youtube.com/playlist?list={object.get('browseId')[2:]}"
    #                 )
    #             ).data

    #             patched_tracks = self._patch_tracks(patch, playlist)

    #             playlist = playlist.model_copy(
    #                 update={
    #                     "uri": f"https://music.youtube.com/playlist?list={object.get('browseId')[2:]}",
    #                     "thumbnail": (
    #                         patch["thumbnails"][0]["url"].split("=")[0]
    #                         if patch.get("thumbnails")
    #                         else None
    #                     ),
    #                     "description": patch.get("description"),
    #                     "tracks": patched_tracks,
    #                 }
    #             )

    #             if only_top:
    #                 return playlist

    #             playlists.append(playlist)

    #         elif object.get("resultType") == "album":
    #             patch = self.client.get_album(object["album"]["id"])

    #             album: Playlist = (
    #                 await self.node.rest.search(
    #                     query=f"https://music.youtube.com/playlist?list={patch['audioPlaylistId']}"
    #                 )
    #             ).data

    #             patched_tracks = self._patch_tracks(patch, album)

    #             album = album.model_copy(
    #                 update={
    #                     "uri": f"https://music.youtube.com/playlist?list={patch['audioPlaylistId']}",
    #                     "thumbnail": (
    #                         patch["thumbnails"][0]["url"].split("=")[0]
    #                         if patch.get("thumbnails")
    #                         else None
    #                     ),
    #                     "description": patch.get("description"),
    #                     "tracks": patched_tracks,
    #                 }
    #             )

    #             if only_top:
    #                 return album

    #             albums.append(album)

    #     validated = LavaSearchLoadingResponse(
    #         tracks=tracks, playlists=playlists, albums=albums, artists=artists
    #     )

    #     return validated
