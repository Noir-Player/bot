"""
### Pool module `main`

This module contains all the pool used in PersikTunes.
"""

from __future__ import annotations

import asyncio
import logging
import random
import re
import time
import traceback
from os import path
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Type,
    Union,
)
from urllib.parse import quote

import aiohttp
import aiohttp.http_exceptions as exceptions
import typing_extensions
from disnake import ClientUser, Interaction, Member, User
from disnake.ext import commands
from spotipy.oauth2 import SpotifyClientCredentials
from websockets import client, exceptions

from . import __version__
from .clients.rest import LavalinkPlayer, LavalinkRest
from .clients.ws import LavalinkWebsocket
from .enums import *
from .enums import LogLevel
from .exceptions import *
from .filters import Filter
from .models.restapi import LavalinkTrackInfo, Playlist, Track
from .routeplanner import RoutePlanner
from .utils import LavalinkVersion, NodeStats, Ping

if TYPE_CHECKING:
    from .player import Player

VERSION_REGEX = re.compile(r"(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:[a-zA-Z0-9_-]+)?")


class Node:
    """The base class for a node.
    This node object represents a Lavalink node.
    `external` arrtibute is an instance for searching tracks via python instead lavalink
    """

    def __init__(
        self,
        *,
        pool: type[NodePool],
        bot: commands.Bot,
        host: str,
        port: int,
        password: str,
        identifier: str,
        secure: bool = False,
        heartbeat: int = 120,
        get_resume_key: Optional[Callable] = None,
        set_resume_key: Optional[Callable] = None,
        get_player_channel: Optional[Callable] = None,
        set_player_channel: Optional[Callable] = None,
        resume_timeout: int = 60,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        session: Optional[aiohttp.ClientSession] = None,
        fallback: bool = False,
        spotify_credentials: Optional[SpotifyClientCredentials] = None,
        log_level: LogLevel = LogLevel.INFO,
        log_handler: Optional[logging.Handler] = None,
        setup_logging: Optional[Callable] = None,
    ):
        if not isinstance(port, int):
            raise TypeError("Port must be an integer")

        self._bot: commands.Bot = bot
        self._host: str = host
        self._port: int = port
        self._pool: type[NodePool] = pool
        self._password: str = password
        self._identifier: str = identifier
        self._heartbeat: int = heartbeat
        self._get_resume_key: Optional[Callable] = get_resume_key
        self._set_resume_key: Optional[Callable] = set_resume_key
        self._get_player_channel: Optional[Callable] = get_player_channel
        self._set_player_channel: Optional[Callable] = set_player_channel
        self._resume_timeout: int = resume_timeout
        self._secure: bool = secure
        self._fallback: bool = fallback
        self._spotify_credentials: Optional[SpotifyClientCredentials] = (
            spotify_credentials
        )

        self._setup_logging = setup_logging or self._setup_logging

        self._log_level: LogLevel = log_level
        self._log_handler = log_handler

        self._rest_uri: str = (
            f"{'https' if self._secure else 'http'}://{self._host}:{self._port}"
        )

        self._session: aiohttp.ClientSession = session  # type: ignore
        self._loop: asyncio.AbstractEventLoop = loop or asyncio.get_event_loop()
        self._task: asyncio.Task = None  # type: ignore

        self._session_id: Optional[str] = None
        self._available: bool = False
        self._version: LavalinkVersion = LavalinkVersion(0, 0, 0)

        self._route_planner = RoutePlanner(self)
        self._log = self._setup_logging(self._log_level)

        if not self._bot.user:
            raise NodeCreationError("Bot user is not ready yet.")

        self._bot_user = self._bot.user

        self._players: Dict[int, Player] = {}

        self.event = asyncio.Event()

        self._websocket = LavalinkWebsocket(
            self,
            self._host,
            self._port,
            self._password,
            self._bot.user.id,
            secure,
            loop,
            fallback,
            log_level=log_level,
            setup_logging=self._setup_logging,
        )

        self._rest = LavalinkRest(
            self,
            self._host,
            self._port,
            self._password,
            self._bot.user.id,
            secure,
            session,
            log_level=log_level,
            setup_logging=self._setup_logging,
        )

    def __repr__(self) -> str:
        return (
            f"<PersikTunes.node ws_uri={self._websocket._websocket_uri} rest_uri={self._rest_uri}"
            f"player_count={len(self._players)}>"
        )

    async def get_resume_key(self) -> str | None:
        if self._get_resume_key:
            return await self._get_resume_key()

    async def set_resume_key(self, resume_key: str | None = None) -> None:
        if self._set_resume_key:
            await self._set_resume_key(resume_key)

    async def get_player_channel(self, guild_id: int):
        if self._get_player_channel:
            return await self._get_player_channel(guild_id)

    async def set_player_channel(self, player: Player, channel_id: int | None = None):
        if self._set_player_channel:
            await self._set_player_channel(player, channel_id)

    @property
    def is_connected(self) -> bool:
        """Property which returns whether this node is connected or not"""
        return self._websocket.is_connected

    # @property
    # def stats(self) -> Any:
    #     """Property which returns the node stats."""
    #     return self._stats

    @property
    def players(self) -> Dict[int, Player]:
        """Property which returns a dict containing the guild ID and the player object."""
        return self._players

    @property
    def bot(self) -> commands.Bot:
        """Property which returns the disnake client linked to this node"""
        return self._bot

    @property
    def player_count(self) -> int:
        """Property which returns how many players are connected to this node"""
        return len(self.players.values())

    @property
    def pool(self) -> type[NodePool]:
        """Property which returns the pool this node is apart of"""
        return self._pool

    @property
    def latency(self) -> float:
        """Property which returns the latency of the node"""
        return Ping(self._host, port=self._port).get_ping()

    @property
    def ping(self) -> float:
        """Alias for `Node.latency`, returns the latency of the node"""
        return self.latency

    @property
    def rest(self) -> LavalinkRest:
        """Property which returns the LavalinkRest object"""
        return self._rest

    def _setup_logging(self, level: LogLevel) -> logging.Logger:
        logger = logging.getLogger("PersikTunes")

        handler = None

        if self._log_handler:
            handler = self._log_handler
            logger.setLevel(handler.level)
        else:
            handler = logging.StreamHandler()
            logger.setLevel(level)
            dt_fmt = "%Y-%m-%d %H:%M:%S"
            formatter = logging.Formatter(
                "[{asctime}] [{levelname:<8}] {name}: {message}",
                dt_fmt,
                style="{",
            )
            handler.setFormatter(formatter)

        if handler:
            logger.handlers.clear()
            logger.addHandler(handler)

        return logger

    async def _handle_version_check(self, version: str) -> None:
        if version.endswith("-SNAPSHOT"):
            # we're just gonna assume all snapshot versions correlate with v4
            self._version = LavalinkVersion(major=4, minor=0, fix=0)
            return

        _version_rx = VERSION_REGEX.match(version)
        if not _version_rx:
            self._available = False
            raise LavalinkVersionIncompatible(
                "The Lavalink version you're using is incompatible. "
                "Lavalink version 3.7.0 or above is required to use this library.",
            )

        _version_groups = _version_rx.groups()
        major, minor, fix = (
            int(_version_groups[0] or 0),
            int(_version_groups[1] or 0),
            int(_version_groups[2] or 0),
        )

        self._log.debug(f"Parsed Lavalink version: {major}.{minor}.{fix}")
        self._version = LavalinkVersion(major=major, minor=minor, fix=fix)
        if self._version < LavalinkVersion(3, 7, 0):
            self._available = False
            raise LavalinkVersionIncompatible(
                "The Lavalink version you're using is incompatible. "
                "Lavalink version 3.7.0 or above is required to use this library.",
            )

        if self._version < LavalinkVersion(4, 0, 0):
            self._log.warn(
                f"Lavalink version {self._version} is not recommended, PersikTunes has been tested with Lavalink 4.0.0 or above."
            )

    async def _configure_resuming(self) -> None:
        data = {"timeout": self._resume_timeout}

        if self._version.major == 3:
            data["resumingKey"] = self._session_id  # type: ignore
        elif self._version.major == 4:
            data["resuming"] = True

        await self.rest.send(
            method="PATCH",
            path=f"sessions/{self._session_id}",
            include_version=True,
            ignore_if_available=True,
            data=data,
        )

    async def connect(self):
        """Initiates a connection with a Lavalink node and adds it to the node pool."""
        await self._bot.wait_until_ready()

        start = time.perf_counter()

        self._session_id = await self.get_resume_key()

        self._log.debug(
            f"Connecting to Lavalink node {self._identifier} with session {self._session_id}"
        )

        if not self.rest._session:
            self.rest._session = aiohttp.ClientSession()

        try:
            version: str = await self.rest.send(
                method="GET",
                path="version",
                ignore_if_available=True,
                include_version=False,
            )

            await self._handle_version_check(version=version)

            self.rest._version = self._version
            self._websocket._version = self._version

            self._log.debug(
                f"Version check from Node {self._identifier} successful. Returned version {version}",
            )

            extra_headers = {  # type: ignore
                "Authorization": self._password,
                "User-Id": self._bot_user.id,
                "Client-Name": f"PersikTunes/{__version__}",
                "Session-Id": self._session_id,
            }

            if self._session_id is None:
                self._log.debug(
                    f"Trying to connect to Node {self._identifier} with no session id"
                )

                del extra_headers["Session-Id"]

            self._websocket._websocket = await client.connect(
                f"{self._websocket._websocket_uri}/v{self._version.major}/websocket",
                extra_headers=extra_headers,
                ping_interval=self._heartbeat,
            )

            if not self._websocket._task:
                self._websocket._task = self._loop.create_task(
                    self._websocket._listen()
                )

            await self.event.wait()

            self._available = True

            if self._version.major == 4:
                if session_id := await self.get_resume_key():
                    self._session_id = session_id

                self._log.debug(f"Trying to reconnect to Node {self._identifier}...")

                if self.player_count:
                    for player in self.players.values():
                        await player._refresh_endpoint_uri(self._session_id)

                elif self._get_player_channel:

                    response = await self.rest.send(
                        method="GET",
                        path=f"sessions/{self._session_id}/players",
                        ignore_if_available=True,
                        include_version=True,
                    )

                    from .player import Player

                    for player in response:
                        player = LavalinkPlayer.model_validate(player)

                        if player.state.connected:
                            channel = await self.get_player_channel(player.guildId)

                            self._log.debug(
                                f"Found player {player.guildId} in guild {channel.id}"  # type: ignore
                            )

                            self._players.update(
                                {
                                    player.guildId: await Player.from_model(
                                        Player(self.bot, channel, node=self), player  # type: ignore
                                    )
                                }
                            )

                            self._log.debug(f"Added player {player.guildId} to list")

                        else:
                            await self.rest.destroy_player(player.guildId)

            self._log.debug(
                f"Node {self._identifier} successfully connected to websocket using {self._websocket._websocket_uri}/v{self._version.major}/websocket",
            )

            end = time.perf_counter()

            self._log.info(
                f"Connected to node {self._identifier}. Took {end - start:.3f}s"
            )
            return self

        except (aiohttp.ClientConnectorError, OSError, ConnectionRefusedError):
            raise NodeConnectionFailure(
                f"The connection to node '{self._identifier}' failed.",
            ) from None
        except exceptions.InvalidHandshake:
            raise NodeConnectionFailure(
                f"The password for node '{self._identifier}' is invalid.",
            ) from None
        except exceptions.InvalidURI:
            raise NodeConnectionFailure(
                f"The URI for node '{self._identifier}' is invalid.",
            ) from None

    async def disconnect(self, fall: bool = False) -> None:
        """Disconnects a connected Lavalink node and removes it from the node pool.
        This also destroys any players connected to the node.
        """

        if fall:
            self._log.error("Failed to connect to Lavalink node.")

        start = time.perf_counter()

        if not self._get_resume_key:
            for player in self.players.copy().values():
                await player.destroy()
                self._log.debug(f"Player {player.id} has been disconnected from node.")  # type: ignore

        await self._websocket._websocket.close()
        await self.rest._session.close()
        self._log.debug("Websocket and http session closed.")

        del self.pool._nodes[self._identifier]
        self._available = False
        self._websocket._task.cancel()

        end = time.perf_counter()
        self._log.info(
            f"Successfully disconnected from node {self._identifier} and closed all sessions. Took {end - start:.3f}s",
        )

    @typing_extensions.deprecated("This method is deprecated; use `rest.send` instead.")
    async def send(
        self,
        method: Literal["GET", "POST", "PATCH", "PUT", "DELETE"],
        path: str,
        include_version: bool = True,
        guild_id: Optional[Union[int, str]] = None,
        query: Optional[str] = None,
        data: Optional[Union[Dict, str]] = None,
        ignore_if_available: bool = False,
    ) -> Any:
        if not ignore_if_available and not self._available:
            raise NodeNotAvailable(
                f"The node '{self._identifier}' is unavailable.",
            )

        uri: str = (
            f"{self._rest_uri}/"
            f'{f"v{self._version.major}/" if include_version else ""}'
            f"{path}"
            f'{f"/{guild_id}" if guild_id else ""}'
            f'{f"?{query}" if query else ""}'
        )

        resp = await self._session.request(
            method=method,
            url=uri,
            json=data or {},
        )
        self._log.debug(
            f"Making REST request to Node {self._identifier} with method {method} to {uri}",
        )
        if resp.status >= 300:
            resp_data: dict = await resp.json()
            raise NodeRestException(
                f'Error from Node {self._identifier} fetching from Lavalink REST api: {resp.status} {resp.reason}: {resp_data["message"]}\n{traceback.print_exc()}',
            )

        if method == "DELETE" or resp.status == 204:
            self._log.debug(
                f"REST request to Node {self._identifier} with method {method} to {uri} completed sucessfully and returned no data.",
            )
            return await resp.json(content_type=None)

        if resp.content_type == "text/plain":
            self._log.debug(
                f"REST request to Node {self._identifier} with method {method} to {uri} completed sucessfully and returned text with body {await resp.text()}",
            )
            return await resp.text()

        self._log.debug(
            f"REST request to Node {self._identifier} with method {method} to {uri} completed sucessfully and returned JSON with body {await resp.json()}",
        )
        return await resp.json()

    def get_player(self, guild_id: int) -> Optional[Player]:
        """Takes a guild ID as a parameter. Returns a PersikTunes Player object or None."""
        return self._players.get(guild_id, None)

    @typing_extensions.deprecated(
        "This method is deprecated; use `rest.build_track` instead."
    )
    async def build_track(
        self,
        identifier: str,
        ctx: Optional[Union[commands.Context, Interaction]] = None,
    ) -> Track:
        """
        Builds a track using a valid track identifier

        You can also pass in a disnake Context object to get a
        Context object on the track it builds.
        """

        data: dict = await self.send(
            method="GET",
            path="decodetrack",
            query=f"encodedTrack={quote(identifier)}",
        )

        return Track.model_validate(data, context={"ctx": ctx})

    # @typing_extensions.deprecated(
    #     "This method is deprecated; use `rest.search` instead."
    # )
    async def search(
        self,
        query: str,
        *,
        ctx: Optional[Union[commands.Context, Interaction]] = None,
        requester: Optional[Union[Member, User, ClientUser]] = None,
        search_type: SearchType = SearchType.ytmsearch,
        filters: Optional[List[Filter]] = None,
    ) -> Optional[Union[Playlist, List[Track]]]:
        """Fetches tracks from the node's REST api to parse into Lavalink.

        If you passed in Spotify API credentials, you can also pass in a
        Spotify URL of a playlist, album or track and it will be parsed accordingly.

        You can pass in a disnake Context object to get a
        Context object on any track you search.

        You may also pass in a List of filters
        to be applied to your track once it plays.
        """

        timestamp = None

        if filters:
            for filter in filters:
                filter.set_preload()

        if URLRegex.DISCORD_MP3_URL.match(query):
            data: dict = await self.rest.send(
                method="GET",
                path="loadtracks",
                query=f"identifier={quote(query)}",
            )

            track: dict = data["tracks"][0]
            track.update({"ctx": ctx, "requester": requester})

            return [Track.model_validate(track)]

        elif path.exists(path.dirname(query)):
            local_file = Path(query)
            data: dict = await self.rest.send(  # type: ignore
                method="GET",
                path="loadtracks",
                query=f"identifier={quote(query)}",
            )

            track: dict = data["tracks"][0]  # type: ignore
            track.update({"ctx": ctx, "requester": requester})

            return [Track.model_validate(track)]

        else:
            if (
                not URLRegex.BASE_URL.match(query)
                and not URLRegex.LAVALINK_SEARCH.match(query)
                and not URLRegex.LAVALINK_REC.match(query)
            ):
                query = f"{search_type}:{query}"

            # If YouTube url contains a timestamp, capture it for use later.

            if match := URLRegex.YOUTUBE_TIMESTAMP.match(query):
                timestamp = float(match.group("time"))

            data = await self.rest.send(
                method="GET",
                path="loadtracks",
                query=f"identifier={quote(query)}",
            )

        load_type = data.get("loadType")

        # Lavalink v4 changed the name of the key from "tracks" to "data"
        # so lets account for that
        data_type = "data" if self._version.major >= 4 else "tracks"

        if not load_type:
            raise TrackLoadError(
                "There was an error while trying to load this track.",
            )

        elif load_type in ("LOAD_FAILED", "error"):
            exception = data.get("exception", data.get("data"))
            raise TrackLoadError(
                f"{exception['message']} [{exception['severity']}]",  # type: ignore
            )

        elif load_type in ("NO_MATCHES", "empty"):
            return None

        elif load_type in ("PLAYLIST_LOADED", "playlist"):
            if self._version.major >= 4:
                track_list = data[data_type]["tracks"]
                playlist_info = data[data_type]["info"]
            else:
                track_list = data[data_type]
                playlist_info = data["playlistInfo"]

            tracks = []

            for track in track_list:
                track.update({"ctx": ctx, "requester": requester})
                tracks.append(Track.model_validate(track))

            return Playlist(
                info=playlist_info,
                tracks=tracks,
                ctx=ctx,
                requester=requester,
                thumbnail=tracks[0].info.artworkUrl,
                uri=query,
            )

        elif load_type in ("SEARCH_RESULT", "TRACK_LOADED", "track", "search"):
            if self._version.major >= 4 and isinstance(data[data_type], dict):
                data[data_type] = [data[data_type]]

            tracks = []

            for track in data[data_type]:
                track.update({"ctx": ctx, "requester": requester})
                tracks.append(Track.model_validate(track))

            return tracks

        else:
            raise TrackLoadError(
                "There was an error while trying to load this track.",
            )

    # @typing_extensions.deprecated(
    #     "This method is deprecated; use `rest.get_recommendations` instead."
    # )
    async def get_recommendations(
        self,
        *,
        track: Track,
        playlist_id: Optional[str] = None,
        additional_seed_tracks: Optional[List[str]] = None,
        ctx: Optional[Union[commands.Context, Interaction]] = None,
        requester: Optional[Union[Member, User, ClientUser]] = None,
        **kwargs,
    ) -> Optional[Union[List[Track], Playlist]]:
        """
        Gets recommendations from either YouTube or Spotify.
        The track that is passed in must be either from
        YouTube or Spotify or else this will not work.
        You can pass in a disnake Context object to get a
        Context object on all tracks that get recommended.
        """
        if track.info.sourceName == TrackType.SPOTIFY.value:

            seed_tracks = (
                track.info.identifier + ",".join(additional_seed_tracks)
                if additional_seed_tracks
                else ""
            )

            query = f"sprec:seed_tracks={seed_tracks}"

            for param in kwargs:
                query += f"&{param}={kwargs.get(param) if type(kwargs.get(param)) == str else ','.split(kwargs.get(param))}"

            return await self.search(query=query, ctx=ctx, requester=requester)

        elif track.info.sourceName == TrackType.YOUTUBE.value:
            if not playlist_id:
                result = await self.rest.abstract_search.relayted(
                    track, ctx=ctx, requester=requester
                )
            else:
                result = await self.rest.abstract_search.relayted(
                    song_or_playlist_id=playlist_id, ctx=ctx, requester=requester
                )

            return result[1:]

        else:
            raise TrackLoadError(
                "The specfied track must be either a YouTube or Spotify track to recieve recommendations.",
            )


class NodePool:
    """The base class for the node pool.
    This holds all the nodes that are to be used by the bot.
    """

    _nodes: Dict[str, Node] = {}

    def __repr__(self) -> str:
        return f"<PersikTunes.NodePool node_count={self.node_count}>"

    @property
    def nodes(self) -> Dict[str, Node]:
        """Property which returns a dict with the node identifier and the Node object."""
        return self._nodes

    @property
    def node_count(self) -> int:
        return len(self._nodes.values())

    @classmethod
    def get_best_node(cls, *, algorithm: NodeAlgorithm) -> Node:
        """Fetches the best node based on an NodeAlgorithm.
        This option is preferred if you want to choose the best node
        from a multi-node setup using either the node's latency
        or the node's voice region.

        Use NodeAlgorithm.by_ping if you want to get the best node
        based on the node's latency.


        Use NodeAlgorithm.by_players if you want to get the best node
        based on how players it has. This method will return a node with
        the least amount of players
        """
        available_nodes: List[Node] = [
            node for node in cls._nodes.values() if node._available
        ]

        if not available_nodes:
            raise NoNodesAvailable("There are no nodes available.")

        if algorithm == NodeAlgorithm.by_ping:
            tested_nodes = {node: node.latency for node in available_nodes}
            return min(tested_nodes, key=tested_nodes.get)  # type: ignore

        elif algorithm == NodeAlgorithm.by_players:
            tested_nodes = {node: len(node.players.keys()) for node in available_nodes}
            return min(tested_nodes, key=tested_nodes.get)  # type: ignore

        else:
            raise ValueError(
                "The algorithm provided is not a valid NodeAlgorithm.",
            )

    @classmethod
    def get_node(cls, *, identifier: Optional[str] = None) -> Node:
        """Fetches a node from the node pool using it's identifier.
        If no identifier is provided, it will choose a node at random.
        """
        available_nodes = {
            identifier: node
            for identifier, node in cls._nodes.items()
            if node._available
        }

        if not available_nodes:
            raise NoNodesAvailable("There are no nodes available.")

        if identifier is None:
            return random.choice(list(available_nodes.values()))

        return available_nodes[identifier]

    @classmethod
    async def create_node(
        cls,
        *,
        bot: commands.Bot,
        host: str,
        port: int,
        password: str,
        identifier: str,
        secure: bool = False,
        heartbeat: int = 120,
        get_resume_key: Optional[Callable] = None,
        set_resume_key: Optional[Callable] = None,
        get_player_channel: Optional[Callable] = None,
        set_player_channel: Optional[Callable] = None,
        resume_timeout: int = 60,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        session: Optional[aiohttp.ClientSession] = None,
        fallback: bool = False,
        log_level: LogLevel = LogLevel.INFO,
        log_handler: Optional[logging.Handler] = None,
        spotify_credentials: Optional[SpotifyClientCredentials] = None,
        setup_logging: Optional[Callable] = None,
    ) -> Node:
        """Creates a Node object to be then added into the node pool.
        For Spotify searching capabilites, pass in valid Spotify API credentials.
        """
        if identifier in cls._nodes.keys():
            raise NodeCreationError(
                f"A node with identifier '{identifier}' already exists.",
            )

        node = Node(
            pool=cls,
            bot=bot,
            host=host,
            port=port,
            password=password,
            identifier=identifier,
            secure=secure,
            heartbeat=heartbeat,
            get_resume_key=get_resume_key,
            set_resume_key=set_resume_key,
            get_player_channel=get_player_channel,
            set_player_channel=set_player_channel,
            resume_timeout=resume_timeout,
            loop=loop,
            session=session,
            fallback=fallback,
            log_level=log_level,
            log_handler=log_handler,
            spotify_credentials=spotify_credentials,
            setup_logging=setup_logging,
        )

        await node.connect()
        cls._nodes[node._identifier] = node
        return node

    @classmethod
    async def disconnect(cls) -> None:
        """Disconnects all available nodes from the node pool."""

        available_nodes: List[Node] = [
            node for node in cls._nodes.values() if node._available
        ]

        for node in available_nodes:
            await node.disconnect()
