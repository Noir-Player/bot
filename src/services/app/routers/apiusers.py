import json

from quart import request, session

from services.database.core import Database
from services.database.models import *
from validators.auth import unauthorized_handler

from ..router import Router

db = Database()

apiusers = Router(
    "apiusers", __name__, template_folder="templates", url_prefix="/api/me"
)


def authorize(obj: dict):
    obj["id"] = int(session["me"].get("id"))
    obj["name"] = session["me"].get("username")
    return obj


def remove_none_values(d: dict):
    return {k: v for k, v in d.items() if bool(v)}


# GET


@apiusers.get("/")
async def me():
    await unauthorized_handler(session)
    return json.dumps(db.users.get_user(int(session["me"].get("id"))))


@apiusers.get("/external/<int:id>")
async def user(id):
    return json.dumps(db.users.get_user(id))


# POST


@apiusers.post("/edit")
async def edit_me():
    await unauthorized_handler(session)
    data = User.model_validate(authorize(await request.get_json()))

    return json.dumps(
        db.users.edit_user(
            int(session["me"].get("id")), data.name, data.description, data.theme
        )
    )


# PATCH


@apiusers.patch("/set-description")
async def set_description():
    await unauthorized_handler(session)
    data = User.model_validate(authorize(await request.get_json()))

    return json.dumps(
        db.users.set_description(data.description, int(session["me"].get("id")))
    )


@apiusers.patch("/set-theme/<string:theme>")
async def set_theme(theme):
    await unauthorized_handler(session)

    return json.dumps(db.users.set_theme(theme, int(session["me"].get("id"))))


def setup(bot):
    apiusers.bot = bot
