from classes.ApiRouter import NOIRouter
from fastapi import Query

router = NOIRouter(prefix="/discovery", tags=["Discovery"])


# GET

@router.get('/')
async def get_discovery(
        count: int = Query(50, ge=1, le=100, description="количество на странице"), 
        page: int = Query(1, ge=1, le=100, description="номер страницы"), 
    ):
    
    playlists = []

    for playlist in router.db.playlists.col().find({"public": True}).skip(count * (page - 1)).limit(count):

        del playlist['_id']
        playlist['forked'] = len(playlist.get('forked', []))

        playlists.append(playlist)

    return {"data": playlists, "meta": {"page": page, "count": count}}


