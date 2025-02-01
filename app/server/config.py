"""FastAPI server configuration."""

import dataclasses
import os
from pathlib import Path

import dotenv
from ufaas_fastapi_business.core import config 

dotenv.load_dotenv()


@dataclasses.dataclass
class Settings(config.Settings):
    """Server config settings."""

    base_dir: Path = Path(__file__).resolve().parent.parent
    base_path: str = "/api/v1/apps"

    USSO_API_KEY: str = os.getenv("USSO_API_KEY")
    USSO_URL: str = os.getenv("USSO_URL", default="https://sso.usso.io")
    USSO_USER_ID: str = os.getenv("USSO_USER_ID")
