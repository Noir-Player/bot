import pprint

from quart import render_template, session

from config import ADMIN_IDS
from services.database.core import Database

from ..router import Router

manage = Router("admin", __name__, static_folder="static", template_folder="templates")


@manage.route("/admin/collection/<string:collection>")
async def admin_users(collection):
    if not session.get("me") or not session["me"].get("id") in ADMIN_IDS:
        return await render_template("errors/403.html"), 403

    values = []

    col = Database().table(collection).find({})

    for value in col:
        pprinted_data = pprint.pformat(value)
        line = pprinted_data.split("\n")
        values.append(line)

    return await render_template("admin/collection.html", values=values)


@manage.route("/admin/session/me")
async def admin_session():
    if not session.get("me") or not session["me"].get("id") in ADMIN_IDS:
        return await render_template("errors/403.html"), 403

    values = []

    pprinted_data = pprint.pformat(session.get("me"))
    line = pprinted_data.split("\n")
    values.append(line)

    return await render_template("admin/sessions.html", values=values)


def setup(bot):
    manage.bot = bot
