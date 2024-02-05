from classes.ApiRouter import NOIRouter
from fastapi import Query

router = NOIRouter(prefix="/playlists", tags=["Playlists"])


# GET

@router.get('/', description="Публичные плейлисты")
async def get_playlists(
    count: int = Query(50, ge=1, le=100, description="количество на странице"),
    page: int = Query(1, ge=1, le=100, description="номер страницы"),
    exclude: str = Query(None, description="исключить значение")
):

    playlists = []

    for playlist in router.db.playlists.col().find(
            {"public": True}).skip(count * (page - 1)).limit(count):

        del playlist['_id']
        playlist['forked'] = len(playlist.get('forked', []))

        if exclude:
            del playlist[exclude]

        playlists.append(playlist)

    return {
        "data": playlists,
        "meta": {
            "page": page,
            "count": count,
            "exclude": exclude}}
