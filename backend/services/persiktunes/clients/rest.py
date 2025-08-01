from typing import TYPE_CHECKING, Any, Callable, Dict, List, Literal, Optional, Union

import aiohttp
from disnake import Interaction, Member, User
from disnake.ext import commands

from .. import __version__
from ..enums import *
from ..exceptions import NodeNotAvailable, NodeRestException
from ..models.restapi import *
from ..models.search import *
from ..models.ws import *
from ..search import YoutubeMusicSearch
from ..utils import LavalinkVersion

if TYPE_CHECKING:  # circular import
    from ..pool import Node


class LavalinkRest:
    def __init__(
        self,
        node: Any,
        host: str,
        port: int,
        password: str,
        user_id: int,
        secure: bool = False,
        session: Optional[aiohttp.ClientSession] = None,
        log_level: LogLevel = LogLevel.INFO,
        setup_logging: Optional[Callable] = None,
    ):
        if not isinstance(port, int):
            raise TypeError("Port must be an integer")

        self._host: str = host
        self._port: int = port
        self._password: str = password
        self._log_level: LogLevel = log_level

        self._secure = secure

        self.node: Any = node

        self._session: aiohttp.ClientSession = session  # type: ignore

        self._version: LavalinkVersion = LavalinkVersion(0, 0, 0)

        self._log = (
            self.node._setup_logging(self._log_level)
            if not setup_logging
            else setup_logging(self._log_level)
        )

        self._rest_uri: str = (
            f"{'https' if self._secure else 'http'}://{self._host}:{self._port}"
        )

        self.user_id = user_id

        self._headers = {
            "Authorization": f"{self._password}",
            "User-Id": f"{self.user_id}",
            "Client-Name": f"PersikTunes/{__version__}",
        }

        self.abstract_search = YoutubeMusicSearch(node=node)

    async def send(
        self,
        method: Literal["GET", "POST", "PATCH", "PUT", "DELETE"],
        path: str,
        include_version: bool = True,
        guild_id: Optional[Union[int, str]] = None,
        query: Optional[str] = None,
        data: Optional[Union[Dict, str, List]] = None,
        ignore_if_available: bool = False,
    ) -> Any:

        if not ignore_if_available and not self.node._available:
            raise NodeNotAvailable(
                f"The node '{self.node._identifier}' is unavailable.",
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
            headers=self._headers,
            json=data or {},
        )
        self._log.debug(
            f"Making REST request to Node {self.node._identifier} with method {method} to {uri}\nRequest data: {data}",
        )
        if resp.status >= 300:
            resp_data: dict = await resp.json()
            raise NodeRestException(
                f'Error from Node {self.node._identifier} fetching from Lavalink REST api: {resp.status} {resp.reason}: {resp_data["message"]}',
            )

        if method == "DELETE" or resp.status == 204:
            self._log.debug(
                f"REST request to Node {self.node._identifier} with method {method} to {uri} completed sucessfully and returned no data.",
            )
            return await resp.json(content_type=None)

        if resp.content_type == "text/plain":
            self._log.debug(
                f"REST request to Node {self.node._identifier} with method {method} to {uri} completed sucessfully and returned text with body {await resp.text()}",
            )
            return await resp.text()

        self._log.debug(
            f"REST request to Node {self.node._identifier} with method {method} to {uri} completed sucessfully and returned JSON with body {await resp.json()}",
        )
        return await resp.json()

    def patch_context(
        self,
        data: Union[Track, Playlist, Album],
        # ctx: Optional[Union[commands.Context, Interaction]] = None,
        # requester: Optional[Union[Member, User]] = None,
        # description: Optional[str] = None,
        # color: Optional[int] = None,
        # tag: Optional[AnyStr] = None,
        **kwargs,
    ):

        update = {
            "ctx": kwargs.get("ctx"),
            "requester": kwargs.get("requester"),
            "description": kwargs.get("description"),
            "color": kwargs.get("color"),
            "tag": kwargs.get("tag"),
        }

        return data.model_copy(
            update={k: v for k, v in update.items() if v is not None}
        )

    async def search(
        self,
        query: str,
        *,
        stype: SearchType = SearchType.ytsearch,
        ctx: Optional[Union[commands.Context, Interaction]] = None,
        requester: Optional[Union[Member, User, str]] = None,
        description: Optional[str] = None,
    ) -> LavalinkTrackLoadingResponse:

        update_ctx = {
            "ctx": ctx,
            "requester": requester,
            "description": description,
        }

        if not re.match(URLRegex.BASE_URL, query):
            query = f"{stype.value}:{query}"

        response = await self.send("GET", f"loadtracks?identifier={query}")
        validated = LavalinkTrackLoadingResponse.model_validate(response)

        if isinstance(validated.data, list):
            data = []

            for track in validated.data:
                data.append(track.model_copy(update=update_ctx))

            validated = validated.model_copy(update={"data": data})

        elif isinstance(validated.data, (Track, Playlist, Album)):
            data = validated.data.model_copy(update=update_ctx)
            validated = validated.model_copy(update={"data": data})

        return validated

    async def decode_track(self, encoded: str) -> LavalinkTrackDecodeResponse:
        response = await self.send("GET", f"decodetrack?encodedTrack={encoded}")
        return LavalinkTrackDecodeResponse.model_validate(response)

    async def decode_tracks(
        self, encoded: List[str]
    ) -> LavalinkTrackDecodeMultiplyResponse:
        response = await self.send("POST", f"decodetracks", data=encoded)
        return LavalinkTrackDecodeMultiplyResponse.model_validate({"tracks": response})

    async def get_players(self) -> List[LavalinkPlayer]:
        response = await self.send("GET", f"sessions/{self.node._session_id}/players")
        return [LavalinkPlayer.model_validate(player) for player in response]

    async def get_player(self, guild_id: int) -> LavalinkPlayer:
        response = await self.send(
            "GET", f"sessions/{self.node._session_id}/players/{guild_id}"
        )
        return LavalinkPlayer.model_validate(response)

    async def update_player(
        self, guild_id: int, data: Union[UpdatePlayerRequest, dict]
    ) -> LavalinkPlayer:

        data = (
            data
            if isinstance(data, UpdatePlayerRequest)
            else UpdatePlayerRequest.model_validate(data)
        )

        if data.track and data.track.userData:  # exclude extra fields
            verified_track = data.track.userData.model_dump(
                include={"encoded", "info", "pluginInfo", "userData"}
            )

            data.track.userData = Track.model_validate(verified_track)

        response = await self.send(
            data.method,
            f"sessions/{self.node._session_id}/players/{guild_id}",
            data=data.model_dump(
                exclude={"method", "noReplace"}, exclude_none=True, exclude_unset=True
            ),
            query=f"noReplace={data.noReplase.__str__().lower()}",
        )

        return LavalinkPlayer.model_validate(response)

    async def destroy_player(self, guild_id: int) -> None:
        await self.send(
            "DELETE",
            f"sessions/{self.node._session_id}/players/{guild_id}",
            ignore_if_available=True,
        )

    async def update_session(self, data: Union[UpdateSessionRequest, dict]) -> None:

        data = (
            data
            if isinstance(data, UpdateSessionRequest)
            else UpdateSessionRequest.model_validate(data)
        )

        await self.send(
            data.method,
            f"sessions/{self.node._session_id}",
            data=data.model_dump(exclude={"method"}),
        )
