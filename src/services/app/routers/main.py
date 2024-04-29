from quart import render_template
from classes.Router import Router

main = Router("main", __name__, static_folder="static")


@main.route("/")
async def index():
    return await render_template("main/index.html")


@main.route("/preview")
async def preview():
    return await render_template("main/preview.html")


@main.route("/terms")
async def terms():
    return await render_template("policy/terms.html")


@main.route("/privacy")
async def privacy():
    return await render_template("policy/privacy.html")


@main.route("/404")
async def not_found_handle():
    return await render_template("errors/404.html")


def setup(bot):
    main.bot = bot
