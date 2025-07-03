from typing import Any, Dict, Optional

from ..enums import URLRegex, YoutubeIdMatchingRegex
from ..models import Album, Artist, Playlist, Track
from .spotify import *
from .template import BaseSearch
from .yandexmusic import *
from .youtubemusic import *


class AbstractSearch(BaseSearch):
    """
    Abstract search class.

    You can use methods without `Node.patch_context`, just pass context in `kwargs` and go:

    ```py
    from persiktunes import AbstractSearch
    ...
    search = AbstractSearch(node = node)
    ...
    @commands.slash_command(description="Play song")
    asyng def play(self, ctx, query: str):
        songs = await search.search_songs(query, ctx=ctx, requester=ctx.author.display_name)
        ...
        await player.play(songs[0])
    """

    def __init__(
        self,
        node: Any,
        default: Union[
            YandexMusicSearch, YoutubeMusicSearch, SpotifySearch
        ] = YoutubeMusicSearch,
        **kwargs,
    ) -> None:
        """Pass a `Node` instance and get started.\nYou can pass any additional kwarg: `language`"""

        self.node = node

        self.youtube = YoutubeMusicSearch(node, **kwargs)

        self.default = default(node, **kwargs)

    async def _call_method(
        self, method_name: str, obj: Any | None = None, *args, **kwargs
    ) -> Any | None:

        if isinstance(obj, Track) or not obj:
            if method_name == "ongoing":
                return getattr(self.default, method_name)(obj, *args, **kwargs)

            return await getattr(self.default, method_name)(obj, *args, **kwargs)

        elif isinstance(obj, str):
            if method_name == "search_suggestions":
                return await getattr(self.default, method_name)(obj, *args, **kwargs)

            if URLRegex.YOUTUBE_URL.match(obj):
                if query := YoutubeIdMatchingRegex.SONG.findall(obj):
                    id = query[0]

                    return await self.youtube.song(id, *args, **kwargs)
                elif query := YoutubeIdMatchingRegex.PLAYLIST.findall(obj):
                    id = query[0]

                    return await self.youtube.playlist(id, *args, **kwargs)

                return await getattr(self.youtube, method_name)(query, *args, **kwargs)

            elif URLRegex.BASE_URL.match(obj):
                return await self.node.rest.search(
                    obj, ctx=kwargs.get("ctx"), requester=kwargs.get("requester")
                )

            else:
                return await self.default.search_songs(obj, *args, **kwargs)

    async def search_songs(
        self, query: str, limit: int = 10, *args, **kwargs
    ) -> Optional[List[Track]] | Any:
        """
        Search for songs.

        Args:
            query: The search query.
            limit: The maximum number of results to return.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            A list of Track objects or None.
        """
        return await self._call_method(
            "search_songs", query, limit=limit, *args, **kwargs
        )

    async def search_albums(
        self, query: str, limit: int = 10, *args, **kwargs
    ) -> Optional[List[Album]] | Any:
        """
        Search for albums.

        Args:
            query: The search query.
            limit: The maximum number of results to return.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            A list of Album objects or None.
        """
        return await self._call_method(
            "search_albums", query, limit=limit, *args, **kwargs
        )

    async def search_playlists(
        self, query: str, limit: int = 10, *args, **kwargs
    ) -> Optional[List[Playlist]] | Any:
        """
        Search for playlists.

        Args:
            query: The search query.
            limit: The maximum number of results to return.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            A list of Playlist objects or None.
        """
        return await self._call_method(
            "search_playlists", query, *args, limit=limit, **kwargs
        )

    async def search_artists(
        self, query: str, *args, **kwargs
    ) -> Optional[List[Artist]] | Any:
        """
        Search for artists.

        Args:
            query: The search query.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            A list of Artist objects or None.
        """
        return await self._call_method("search_artists", query, *args, **kwargs)

    async def search_suggestions(
        self, query: str, *args, **kwargs
    ) -> Optional[List[str]] | Any:
        """
        Autocomplete your search from default service.

        Args:
            query (str): The search query.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            A list of suggestions or None.
        """
        return await self._call_method("search_suggestions", query, *args, **kwargs)

    async def search(
        self, query: str, limit: int = 1, *args, **kwargs
    ) -> Optional[List[Track]] | Any:
        """
        Legacy provider for search_songs.

        This method is kept for backward compatibility.
        It calls `search_songs` method with the given query and limit.

        Args:
            query: The search query.
            limit: The maximum number of results to return.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            A list of Track objects or None.
        """
        return await self.search_songs(query, limit=limit, *args, **kwargs)

    async def song(self, id: str, *args, **kwargs) -> Optional[Track]:
        """
        Get song by id.

        Args:
            id: The id of the song.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            A Track object or None.
        """
        return await self._call_method("song", id, *args, **kwargs)

    async def album(self, id: str, *args, **kwargs) -> Optional[Album]:
        """
        Get album by id.

        Args:
            id: The id of the album.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            An Album object or None.
        """
        return await self._call_method("album", id, *args, **kwargs)

    async def playlist(self, id: str, *args, **kwargs) -> Optional[Playlist]:
        """
        Get playlist by id.

        Args:
            id: The id of the playlist.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            A Playlist object or None.
        """
        return await self._call_method("playlist", id, *args, **kwargs)

    async def artist(self, id: str, *args, **kwargs) -> Optional[Artist]:
        """
        Get artist by id.

        Args:
            id: The id of the artist.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            An Artist object or None.
        """
        return await self._call_method("artist", id, *args, **kwargs)

    async def moods(self, *args, **kwargs) -> Optional[List[Mood]]:
        """
        Get all moods from default service.

        Args:
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            A list of moods or None.
        """
        return await self._call_method("moods", *args, **kwargs)

    async def get_mood_playlists(
        self, mood: Mood, *args, **kwargs
    ) -> Optional[Playlist]:
        """
        Get mood playlists from default service.

        Args:
            mood: The mood of the playlists.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            A Playlist object or None.
        """
        return await self._call_method("get_mood_playlists", mood, *args, **kwargs)

    async def lyrics(self, song: Track, *args, **kwargs) -> Optional[Track]:
        """
        Get lyrics for song.

        Args:
            song: The Track object for which to get lyrics.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            A Track object with lyrics or None.
        """
        return await self._call_method("lyrics", song, *args, **kwargs)

    async def related(
        self, song: Track, limit: int = 10, *args, **kwargs
    ) -> Optional[List[Track]]:
        """
        Get related songs for song.

        Args:
            song: The Track object for which to get related songs.
            limit: The maximum number of results to return.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            A list of Track objects or None.
        """
        return await self._call_method("related", song, limit, *args, **kwargs)

    @staticmethod
    async def ongoing(
        song: Track,  # The Track object for which to generate the ongoing playlist.
        limit: int = 40,  # The maximum number of tracks to include in the ongoing playlist.
        *args,  # Additional positional arguments.
        **kwargs,  # Additional keyword arguments.
    ) -> AsyncGenerator[Track, None]:
        """
        Generate an ongoing playlist for a given song.

        Args:
            song: The Track object for which to generate the ongoing playlist.
            limit: The maximum number of tracks to include in the ongoing playlist.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Yields:
            A Track object representing the next track in the ongoing playlist.

        Returns:
            None
        """
        return await AbstractSearch._call_method(
            "ongoing", song, limit, *args, **kwargs
        )
