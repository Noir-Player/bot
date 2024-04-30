import pomice
from api.shemas import *
from fastapi import Cookie, Query, Response

from services.api.router import NOIRouter

router = NOIRouter(prefix="/discovery", tags=["Discovery"])


# GET


@router.get("/", description="Получить путеводитель", response_model=DiscoveryResponse)
async def get_discovery(
    sessionid: str = Cookie(),
):

    pass


@router.get(
    "/search",
    description="Поиск треков, плейлистов",
    response_model=DiscoverySearchResponse,
)
async def search(
    sessionid: str = Cookie(),
    query: str = Query("", description="Запрос / ссылка"),
    type: Literal["spsearch", "ytsearch", "ytmsearch", "scsearch", "dzsearch"] = Query(
        "ytmsearch", description="Тип поиска"
    ),
):
    await router.session.verify(sessionid)

    only = tracks = playlists = mixes = None

    node: pomice.Node = router.bot.node

    user_playlists = router.db.playlists.find(query)

    search_result = router.execute(
        node.get_tracks(query, search_type=pomice.SearchType(type))
    )

    if not search_result:
        return Response(
            content="Tracks, playlists and mixes not found", status_code=404
        )

    if hasattr(search_result, "tracks"):
        playlists = [search_result.to_dict()]
        only = "playlist"

    else:
        tracks = [track.to_dict() for track in search_result]

        if len(search_result) == 1:
            only = "track"

    mixes = node.external.get_mixes("sp" if type == "spsearch" else "yt")

    return {
        "tracks": tracks,
        "playlists": playlists,
        "user_playlists": user_playlists,
        "mixes": mixes,
        "meta": {"query": query, "type": type, "only": only},
    }
