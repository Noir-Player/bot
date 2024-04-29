from quart import render_template
from routers.apiplaylists import apiplaylists
from routers.apiservers import apiservers
from routers.apistars import apistars
from routers.apiusers import apiusers
from routers.main import main
from routers.manage import manage
from routers.me import me
from routers.oauth import oauth
from routers.playlists import playlists
from routers.setups import setups
from routers.wsplayers import players

from classes.Router import App
from src.config import OAUTH2_CLIENT_SECRET


def setup(bot) -> App:
    app = App(__name__, bot=bot)

    app.config["SECRET_KEY"] = OAUTH2_CLIENT_SECRET

    app.register_blueprint(main)
    app.register_blueprint(playlists)
    app.register_blueprint(oauth)
    app.register_blueprint(me)
    app.register_blueprint(setups)
    app.register_blueprint(manage)

    app.register_blueprint(apiplaylists)
    app.register_blueprint(apistars)
    app.register_blueprint(apiusers)
    app.register_blueprint(apiservers)

    app.register_blueprint(players)

    app.register_error_handler(404, not_found)
    app.register_error_handler(500, internal_error)

    return app


async def not_found(error):
    return await render_template("errors/404.html", error=error), 404


async def internal_error(error):
    return await render_template("errors/500.html", error=error), 500
