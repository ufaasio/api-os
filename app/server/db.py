from apps.base.models import BaseEntity
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from utils.basic import get_all_subclasses

from .config import Settings


async def init_db():
    client = AsyncIOMotorClient(Settings.mongo_uri)
    db = client.get_database(Settings.project_name)
    await init_beanie(
        database=db,
        document_models=[
            cls
            for cls in get_all_subclasses(BaseEntity)
            if not (
                hasattr(cls, "Settings")
                and getattr(cls.Settings, "__abstract__", False)
            )
        ],
    )
    return db
