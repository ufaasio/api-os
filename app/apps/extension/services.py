from server.config import Settings
from utils.aionetwork import aio_request


async def get_app_credentials():
    api_key = Settings.USSO_API_KEY
    sso_url = Settings.USSO_URL

    return await aio_request(
        method="post",
        url=f"{sso_url}/app-auth/register",
        headers={"x-api-key": api_key},
    )
