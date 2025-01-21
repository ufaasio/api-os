import httpx
from fastapi import APIRouter, Query, Request, Response
from fastapi_mongo_base.core import exceptions
from fastapi_mongo_base.schemas import PaginatedResponse
from server.config import Settings
from ufaas_fastapi_business.middlewares import get_business
from ufaas_fastapi_business.models import Business
from ufaas_fastapi_business.routes import AbstractAuthRouter
from usso.fastapi import jwt_access_security

from .models import Extension, Installed, Permission
from .schemas import AppSchema, PermissionSchema


class PermissionsRouter(AbstractAuthRouter[Permission, PermissionSchema]):
    def __init__(self):
        super().__init__(
            model=Permission,
            schema=PermissionSchema,
            user_dependency=None,
        )

    # TODO


class ExtensionRouter(AbstractAuthRouter[Extension, AppSchema]):
    def __init__(self):
        super().__init__(
            model=Extension,
            schema=AppSchema,
            user_dependency=None,
            # prefix="/apps",
            # tags=["Applications"],
        )

    # TODO


class InstalledRouter(AbstractAuthRouter[Installed, AppSchema]):
    def __init__(self):
        super().__init__(
            model=Installed,
            schema=AppSchema,
            user_dependency=jwt_access_security,
            # prefix="/apps",
            # tags=["Applications"],
        )

    # TODO

    async def list_items(
        self,
        request: Request,
        offset: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=Settings.page_max_limit),
        type: str = Query(None),
    ):
        auth = await self.get_auth(request)
        import logging

        logging.info(f"List items {offset=}, {limit=}, {type=}, {auth.user_id=}")
        limit = max(1, min(limit, Settings.page_max_limit))

        items, total = await self.model.list_total_combined(
            user_id=auth.user_id,
            business_name=auth.business.name,
            offset=offset,
            limit=limit,
            type=type,
        )
        items_in_schema = [self.list_item_schema(**item.model_dump()) for item in items]

        return PaginatedResponse(
            items=items_in_schema,
            total=total,
            offset=offset,
            limit=limit,
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
    import logging

    logging.info(f"Proxying request to {app_name}/{path}")
    business: Business = await get_business(request)

    app: Installed = await Installed.find_one(
        Installed.name == app_name, Installed.business_name == business.name
    )
    if not app:
        raise exceptions.BaseHTTPException(
            status_code=404,
            error="Not Found",
            message=f"Extension {app_name} not found",
        )

    url = f"{app.domain}/api/v1/apps/{app.name}/{path}"

    headers = dict(request.headers)
    headers["x-original-host"] = request.url.hostname
    headers.pop("host", None)
    body = await request.body()

    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                params=request.query_params,
                content=body,
                timeout=None,
            )
            return Response(
                status_code=response.status_code,
                content=response.content,
                headers=dict(response.headers),
            )
    except httpx.HTTPStatusError as e:
        return Response(
            status_code=e.response.status_code,
            content=e.response.content,
            headers=dict(e.response.headers),
        )
    except Exception as e:
        return Response(
            status_code=500,
            content=str(e),
            headers={},
        )


@router.get("/{app_name}/{path:path}")
async def get_app(request: Request, app_name: str, path: str):
    import logging

    logging.info(f"GET {app_name}/{path}")

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
