"""
## Routers Module
import all routers in here
"""

import importlib
from os import listdir

from fastapi import FastAPI

def include_modules(app: FastAPI, bot):

    for filename in listdir("./api/routers"):
        if filename.endswith(".py") and not filename.startswith("__"):
            
            routerfile = importlib.import_module(f'api.routers.{filename[:-3]}')

            router = routerfile.router

            router.bot = bot

            app.include_router(router)
