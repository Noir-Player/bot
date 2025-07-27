from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from services.database import get_documents
from .config import get_instance as get_settings

motor = None
beanie_inited = False


def get_motor():
    global motor

    if motor is None:
        motor = AsyncIOMotorClient(
            f"mongodb://{get_settings().mongodb_host}:{get_settings().mongodb_port}"
        ).get_database(f"NoirApp-{get_settings().mode}-{get_settings().version}")

    return motor


async def init():
    global beanie_inited

    if not beanie_inited:
        await init_beanie(database=get_motor(), document_models=get_documents())

        beanie_inited = True
