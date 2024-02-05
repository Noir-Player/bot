from fastapi import FastAPI
import api.routers as routers
import api.shemas as shemas

import uuid

from config import UUID_STRING


class NoirAPI(FastAPI):

    @property
    def salt(self) -> str:
        return uuid.uuid5(uuid.NAMESPACE_X500, UUID_STRING).__str__()


def __init__(bot) -> NoirAPI:
    """Return pathed FastAPI obj"""
    api = NoirAPI(
        title="Noir Player API",
        description="Noir Player API app. Simple, Graceful and Powerful discord player",
        version="0.2.0",
        docs_url="/do-api-reference",
        redoc_url="/api-reference",
        root_path="/dev",
        openapi_url="/openapi.json")

    routers.include_modules(api, bot)

    return api
