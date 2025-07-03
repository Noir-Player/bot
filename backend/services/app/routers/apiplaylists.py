import json
import traceback

import pomice
from quart import request, session

from services.database.core import Database
from services.database.models import *
from validators.auth import unauthorized_handler

from ..router import Router

db = Database()

apiplaylists = Router(
    "apiplaylists", __name__, template_folder="templates", url_prefix="/api/playlists"
)


def authorize(obj: dict):
    obj["author"] = {
        "id": int(session["me"].get("id")),
        "name": session["me"].get("username"),
    }
    return obj


def remove_none_values(d: dict):
    return {k: v for k, v in d.items() if bool(v)}


# GET


@apiplaylists.get("/")
async def my_playlists():
    await unauthorized_handler(session)

    usrplaylists = []

    for playlist in db.playlists.get_user_playlists(int(session["me"].get("id"))):

        del playlist["_id"]
        usrplaylists.append(playlist)

    return json.dumps(usrplaylists)


@apiplaylists.get("/<string:uuid>")
async def get_playlist(uuid):
    return json.dumps(db.playlists.get_playlist(uuid))


# POST


@apiplaylists.post("/create")
async def create_playlist():
    await unauthorized_handler(session)
    playlist = Playlist.model_validate(authorize(await request.get_json()))

    return json.dumps(
        db.playlists.create_playlist(
            id=int(session["me"].get("id")),
            name=session["me"].get("username"),
            **playlist.model_dump()
        )
    )


# PATCH


@apiplaylists.patch("/<string:uuid>/edit")
async def edit_playlist(uuid):
    try:
        await unauthorized_handler(session)
        playlist = Playlist.model_validate(authorize(await request.get_json()))

        return json.dumps(
            db.playlists.edit_playlist(
                uuid=uuid,
                id=int(session["me"].get("id")),
                **playlist.model_dump(
                    exclude=[
                        "uuid",
                        "author",
                        "tracks",
                        "tracks",
                        "metric",
                        "forked",
                        "integer",
                    ]
                )
            )
        )
    except:
        traceback.print_exc()


@apiplaylists.patch("/<string:uuid>/add-track")
async def add_to_playlist(uuid):
    await unauthorized_handler(session)
    try:
        data = AddTrackRequest.model_validate(await request.get_json())

        query = apiplaylists.execute(apiplaylists.bot.node.get_tracks(data.query))

        if type(query) == pomice.Playlist:
            tracks = query.tracks

            track = {
                "$each": [
                    apiplaylists.bot.build.track(track.info, track.track_type.value)
                    for track in tracks
                ]
            }

        elif query:
            track = apiplaylists.bot.build.track(
                query[0].info, query[0].track_type.value
            )

        result = db.playlists.add_to_playlist(
            uuid=uuid, id=int(session["me"].get("id")), track=track
        )

        return json.dumps(False if not result else track)
    except:
        traceback.print_exc()


@apiplaylists.patch("/<string:uuid>/remove-track")
async def remove_track(uuid):
    await unauthorized_handler(session)
    data = RemoveTrackRequest.model_validate(await request.get_json())

    return json.dumps(
        db.playlists.remove_from_playlist(uuid, int(session["me"].get("id")), data.url)
    )


@apiplaylists.patch("/<string:uuid>/move-track")
async def move_track(uuid):
    await unauthorized_handler(session)
    data = MoveTrackRequest.model_validate(await request.get_json())

    return json.dumps(
        db.playlists.move_track(uuid, data.url, data.pos, int(session["me"].get("id")))
    )


@apiplaylists.patch("/merge")
async def merge_playlists():
    await unauthorized_handler(session)
    data = MergePlaylistsRequest.model_validate(await request.get_json())

    return json.dumps(
        db.playlists.merge_playlists(
            data.uuid1, data.uuid2, int(session["me"].get("id"))
        )
    )


@apiplaylists.patch("/<string:uuid>/add-to-library")
async def add_to_library(uuid):
    await unauthorized_handler(session)
    return json.dumps(db.playlists.add_to_library(uuid, int(session["me"].get("id"))))


# DELETE


@apiplaylists.delete("/<string:uuid>/delete")
async def delete_playlist(uuid):
    await unauthorized_handler(session)
    return json.dumps(db.playlists.delete_playlist(uuid, int(session["me"].get("id"))))


def setup(bot):
    apiplaylists.bot = bot
