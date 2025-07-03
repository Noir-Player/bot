from api.shemas import *
from fastapi import Query

from services.api.router import NOIRouter

router = NOIRouter(prefix="/playlists", tags=["Playlists"])


# GET


@router.get("/", description="Публичные плейлисты", response_model=PlaylistsResponse)
async def get_playlists(
    count: int = Query(50, ge=1, le=100, description="количество на странице"),
    page: int = Query(1, ge=1, description="номер страницы"),
):

    playlists = []

    for playlist in (
        router.db.playlists.col()
        .find({"public": True})
        .skip(count * (page - 1))
        .limit(count)
    ):

        del playlist["_id"]
        playlist["forked"] = len(playlist.get("forked", []))

        playlists.append(playlist)

    return {"data": playlists, "meta": {"page": page, "count": count}}
