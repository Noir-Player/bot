import datetime
import json
import re
from random import shuffle

import bleach
import markdown
from bson.objectid import ObjectId
from quart import render_template, session

from services.database.core import Database

from ..router import Router

tags = [
    "abbr",
    "acronym",
    "b",
    "blockquote",
    "code",
    "em",
    "i",
    "li",
    "ol",
    "strong",
    "ul",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "p",
]
attrs = ["class"]

db = Database()

playlists = Router("playlists", __name__, template_folder="templates")


def sort_by_len(playlist):
    return len(playlist.get("tracks", ""))


def sort_by_add(playlist):
    return len(playlist.get("forked", []))


# Main block


@playlists.route("/playlists")
async def main():
    playlists, singles = [], []

    for playlist in db.playlists.table.find({"public": True}):
        if len(playlist.get("tracks", [])) == 1:
            singles.append(playlist)

        elif len(playlist.get("tracks", [])):
            playlists.append(playlist)

    playlists.sort(reverse=True, key=sort_by_add)
    singles.sort(reverse=True, key=sort_by_add)

    # for playlist in playlists_arr:
    #     playlists_arr[playlists_arr.index(playlist)]['notes'] = markdown.markdown(playlist.get('notes', ''))

    return await render_template(
        "main/playlists.html",
        playlists=playlists,
        singles=singles,
        len=len,
        shuffle=shuffle,
    )


@playlists.route("/playlists/<string:uuid>")
async def view_playlist(uuid):

    playlist = db.playlists.get_playlist(uuid)

    if not playlist:
        return await render_template("errors/404.html"), 404

    count = str(len(playlist.get("forked"))) if playlist.get("forked") else "0"

    if playlist.get("description"):
        url_regex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"

        playlist["html_notes"] = bleach.clean(
            re.sub(url_regex, "", markdown.markdown(playlist.get("description"))),
            tags=tags,
            attributes=attrs,
        )

    user_playlists = (
        db.playlists.get_user_playlists(int(session["me"].get("id")), False)
        if session.get("me")
        else None
    )

    if not session.get("me") or not db.cache.get(int(session["me"].get("id"))):
        add = remove = edit = False
    else:
        edit = int(session["me"].get("id")) == int(playlist.get("author").get("id"))
        remove = edit or (
            int(session["me"].get("id")) in playlist.get("forked")
            if playlist.get("forked")
            else False
        )
        add = not remove

    return await render_template(
        "main/playlist.html",
        playlist=playlist,
        len=len,
        addable=add,
        removable=remove,
        editable=edit,
        add_count=count,
        playlists=user_playlists,
        timestamp=ObjectId(playlist.get("_id")).generation_time.date(),
        datetime=datetime,
    )


def setup(bot):
    playlists.bot = bot
