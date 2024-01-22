from quart import session, request
import json, pomice, traceback

from checks.check_auth import unauthorized_handler

from classes.WebModels import *

from classes.Router import Router

from clients.database import Database

db = Database()

apistars = Router("apistars", __name__, template_folder="templates", url_prefix="/api/stars")

def authorize(obj: dict):
    obj['user_id'] = int(session['me'].get('id'))
    return obj

def remove_none_values(d: dict):
    return {k: v for k, v in d.items() if bool(v)}

# GET

@apistars.get('/')
async def my_stars():
    await unauthorized_handler(session)
    return json.dumps(db.stars.get_stars(int(session['me'].get('id'))))

# PATCH

@apistars.patch('/add-track')
async def add_to_playlist():
    await unauthorized_handler(session)
    data = AddTrackRequest.model_validate(await request.get_json())

    query = apistars.execute(apistars.bot.node.get_tracks(data.query))

    if type(query) == pomice.Playlist:
        track = query.tracks

    elif query:
        track = query[0]

    track = apistars.bot.build.track(track.info, track.track_type.value)

    result = db.stars.add_to_stars(id=int(session['me'].get('id')), track_or_list=track)

    return json.dumps(False if not result else track)

@apistars.patch('/remove-track')
async def remove_track():
    await unauthorized_handler(session)
    data = RemoveTrackRequest.model_validate(await request.get_json())

    return json.dumps(db.stars.remove_from_stars(data.url, int(session['me'].get('id'))))

@apistars.patch('/move-track')
async def move_track():
    await unauthorized_handler(session)
    data = MoveTrackRequest.model_validate(await request.get_json())

    return json.dumps(db.stars.move_track(data.url, data.pos, int(session['me'].get('id'))))

def setup(bot):
    apistars.bot = bot