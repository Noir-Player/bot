from quart import render_template

from config import OAUTH2_CLIENT_SECRET
from services.app.router import App
from services.app.routers.apiplaylists import apiplaylists
from services.app.routers.apiservers import apiservers
from services.app.routers.apistars import apistars
from services.app.routers.apiusers import apiusers
from services.app.routers.main import main
from services.app.routers.manage import manage
from services.app.routers.me import me
from services.app.routers.oauth import oauth
from services.app.routers.playlists import playlists
from services.app.routers.setups import setups
from services.app.routers.wsplayers import players


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
