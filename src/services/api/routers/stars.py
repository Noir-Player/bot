from classes.ApiRouter import NOIRouter
from fastapi import Query, Cookie, Response
from api.shemas import *

router = NOIRouter(prefix="/stars", tags=["Stars"])


# GET

@router.get('/', description="Ваши звездочки", response_model=StarsResponse)
async def get_stars(
    sessionid: str = Cookie(),
    count: int = Query(50, ge=1, le=100, description="количество на странице"),
    page: int = Query(1, ge=1, description="номер страницы"),
):

    stars = router.db.stars.get_stars(
        int(router.db.sessions.get(sessionid).get("id"))
    ) or {}

    stars['tracks'] = stars.get("tracks", [])[page * (count - 1):][:page]

    return {
        "data": stars,
        "meta": {
            "page": page,
            "count": count
            }}


@router.patch('/', description="Переместить трек", status_code=204)
async def move(
    sessionid: str = Cookie(),
    pos1: int = Query(ge=0, le=500, description="Исходная позиция трека"),
    pos2: int = Query(ge=0, description="Позиция, на которую нужно переместить"),
):

    return Response(status_code=204)


@router.get('/{index}', description="Трек из звездочек", response_model=StarsTrackResponse)
async def get_track(
    index: int,
    sessionid: str = Cookie()
    ):

    stars = router.db.stars.get_stars(
        int(router.db.sessions.get(sessionid).get("id"))
    ) or {}

    return stars.get("tracks", [])[index]