from fastapi import FastAPI
import api.routers as routers

def __init__(bot) -> FastAPI:
    """Return pathed FastAPI obj"""
    app = FastAPI(
        title="Noir Player API",
        description="Noir Player API app, works on sessions without JWT",
        version="0.1.0"
    )

    routers.include_modules(app, bot)

    return app
