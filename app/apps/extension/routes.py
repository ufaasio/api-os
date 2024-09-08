import aiohttp
from apps.business.middlewares import get_business
from apps.business.models import Business
from apps.business.routes import AbstractBusinessBaseRouter
from core import exceptions
from fastapi import APIRouter, Request, Response
from usso.fastapi import jwt_access_security

from .models import Extension, Installed, Permission
from .schemas import AppSchema, PermissionSchema


class PermissionsRouter(AbstractBusinessBaseRouter[Permission, PermissionSchema]):
    def __init__(self):
        super().__init__(
            model=Permission,
            schema=PermissionSchema,
            user_dependency=None,
        )


class ExtensionRouter(AbstractBusinessBaseRouter[Extension, AppSchema]):
    def __init__(self):
        super().__init__(
            model=Extension,
            schema=AppSchema,
            user_dependency=None,
            # prefix="/apps",
            # tags=["Applications"],
        )


class InstalledRouter(AbstractBusinessBaseRouter[Installed, AppSchema]):
    def __init__(self):
        super().__init__(
            model=Installed,
            schema=AppSchema,
            user_dependency=jwt_access_security,
            # prefix="/apps",
            # tags=["Applications"],
        )


extension_router = ExtensionRouter().router
permission_router = PermissionsRouter().router
installed_router = InstalledRouter().router

router = APIRouter()
router.include_router(extension_router)
router.include_router(permission_router)
router.include_router(installed_router)


async def proxy_request(
    request: Request,
    app_name: str,
    path: str,
    method: str,
):
    business: Business = await get_business(request)

    app: Extension = await Extension.find_one(
        Extension.name == app_name, Extension.business_name == business.name
    )
    if not app:
        raise exceptions.BaseHTTPException(
            status_code=404,
            error="Not Found",
            message=f"Extension {app_name} not found",
        )

    url = f"{app.url}/{path}"
    async with aiohttp.ClientSession() as session:
        async with session.request(
            method=method,
            url=url,
            headers=request.headers,
            params=request.query_params,
            data=await request.body() if method in ["POST", "PUT", "PATCH"] else None,
        ) as response:
            content = await response.read()
            return Response(
                status_code=response.status,
                content=content,
                headers=dict(response.headers),
            )


@router.get("/{app_name}/{path:path}")
async def get_app(request: Request, app_name: str, path: str):
    return await proxy_request(request, app_name, path, "GET")


@router.post("/{app_name}/{path:path}")
async def post_app(request: Request, app_name: str, path: str):
    return await proxy_request(request, app_name, path, "POST")


@router.put("/{app_name}/{path:path}")
async def put_app(request: Request, app_name: str, path: str):
    return await proxy_request(request, app_name, path, "PUT")


@router.delete("/{app_name}/{path:path}")
async def delete_app(request: Request, app_name: str, path: str):
    return await proxy_request(request, app_name, path, "DELETE")


@router.patch("/{app_name}/{path:path}")
async def patch_app(request: Request, app_name: str, path: str):
    return await proxy_request(request, app_name, path, "PATCH")
