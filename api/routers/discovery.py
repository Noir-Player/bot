from classes.ApiRouter import NOIRouter
from fastapi import Query, Cookie

from api.shemas import *

router = NOIRouter(prefix="/discovery", tags=["Discovery"])


# GET

@router.get('/', description="Получить путеводитель", response_model=DiscoveryResponse)
async def get_discovery(
    sessionid: str = Cookie(),
    count: int = Query(50, ge=1, le=100, description="количество на странице"),
    page: int = Query(1, ge=1, description="номер страницы"),
):

    playlists = []

    for playlist in router.db.playlists.col().find(
            {"public": True}).skip(count * (page - 1)).limit(count):

        del playlist['_id']
        playlist['forked'] = len(playlist.get('forked', []))

        playlists.append(playlist)

    return {"data": playlists, "meta": {"page": page, "count": count}}



@router.get('/search', description="Поиск треков, плейлистов", response_model=DiscoverySearchResponse)
async def search(
    sessionid: str = Cookie(),
    query: str = Query('', description="Запрос / ссылка"),
    type: Optional[Literal["spsearch", "ytsearch", "ytmsearch", "scsearch", "dzsearch"]] = Query("spsearch", description="Тип поиска")
):
    return {}