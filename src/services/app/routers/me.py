import datetime
import traceback

from quart import redirect, render_template, session

from services.database.core import Database

from ..router import Router

me = Router("me", __name__, template_folder="templates")
db = Database()


def sort_by_len(playlist):
    return len(playlist.get("tracks", ""))


@me.route("/me")
async def main():
    if not session.get("me") or not db.cache.get(int(session["me"].get("id"))):
        return redirect("/oauth")

    playlists_arr = db.playlists.get_user_playlists(int(session["me"].get("id")))

    servers: dict = db.cache.get(int(session["me"].get("id"))).get("guilds")

    fastpicks = db.metrics.get_metric(int(session["me"].get("id")))

    try:
        return await render_template(
            "main/me.html",
            servers=servers.get("other", [])[:4],
            fastpicks=fastpicks.get("last_tracks", [])[::-1] if fastpicks else [],
            playlists=playlists_arr[::-1][:4],
            user=db.users.get_user(int(session["me"].get("id"))),
            datetime=datetime,
        )
    except:
        traceback.print_exc()


# ---------------------------------------------------------------------------------------------------------


@me.route("/me/playlists")
async def playlists():
    if not session.get("me") or not db.cache.get(int(session["me"].get("id"))):
        return redirect("/oauth")

    playlists_arr = []

    results = db.playlists.get_user_playlists(int(session["me"].get("id")))

    for playlist in results:
        playlists_arr.append(playlist)

    return await render_template("main/my_playlists.html", playlists=playlists_arr)


# ---------------------------------------------------------------------------------------------------------


@me.route("/me/stars")
async def stars():
    if not session.get("me") or not db.cache.get(int(session["me"].get("id"))):
        return redirect("/oauth")

    stars = db.stars.get_stars(int(session["me"].get("id")))

    return await render_template("main/stars.html", stars=stars, datetime=datetime)


# ---------------------------------------------------------------------------------------------------------


def setup(bot):
    me.bot = bot
