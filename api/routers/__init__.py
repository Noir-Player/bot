"""
## Routers Module
import all routers in here
"""

import importlib
from os import listdir

from fastapi import FastAPI
from utils.printer import *


def include_modules(app: FastAPI, bot):

    for filename in listdir("./api/routers"):
        if filename.endswith(".py") and not filename.startswith(
                "_"):  # only routers without specials

            routerfile = importlib.import_module(
                f'api.routers.{filename[:-3]}')

            try:

                router = routerfile.router

                router.bot, router.salt = bot, app.salt

                app.include_router(router)

            except Exception as e:

                lprint(
                    f"Routerfile {routerfile.__name__} has no router variable or {e}",
                    Color.red,
                    "RLOADER")
