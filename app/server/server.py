from apps.extension.routes import router as apps_router
from core.middlewares import DynamicCORSMiddleware
from fastapi_mongo_base.core import app_factory

from . import config

app = app_factory.create_app(
    settings=config.Settings(),
    ufaas_handler=False,
)

app.add_middleware(DynamicCORSMiddleware)
app.include_router(apps_router, prefix=f"{config.Settings.base_path}")
