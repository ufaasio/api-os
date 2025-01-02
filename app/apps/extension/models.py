import uuid

from beanie.odm.queries.find import FindMany
from fastapi_mongo_base.models import BaseEntity, BusinessEntity, OwnedEntity
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from .schemas import AppDomainSchema, AppSchema, AuthorizedDomainSchema


class Permission(BaseEntity):
    scope: str = Field(
        description="Permission scope",
        json_schema_extra={"index": True, "unique": True},
    )
    description: str | None = None

    class Settings:
        indexes = [
            IndexModel([("scope", ASCENDING)], unique=True),
        ]


class Extension(AppSchema, OwnedEntity):
    api_doc_url: str
    is_active: bool = False
    needed_data: dict = {}

    description: str | None = None
    logo: str | None = None
    is_published: bool = False

    support_email: str | None = None
    app_domain_info: AppDomainSchema = AppDomainSchema()
    developer_contact_emails: list[str] = []

    authorized_domains: AuthorizedDomainSchema = AuthorizedDomainSchema()
    test_users: list[uuid.UUID | str] = []
    permissions: list[str] = []

    class Settings:
        indexes = OwnedEntity.Settings.indexes + [
            IndexModel([("name", ASCENDING)], unique=True),
            IndexModel([("domain", ASCENDING)], unique=True),
        ]

    @classmethod
    def create_exclude_set(cls) -> list[str]:
        return super().create_exclude_set() + ["is_active"]


class Installed(AppSchema, BusinessEntity):
    is_active: bool = True
    permissions: list[str] = []

    class Settings:
        indexes = BusinessEntity.Settings.indexes + [
            IndexModel(
                [("name", ASCENDING), ("business_name", ASCENDING)], unique=True
            ),
            IndexModel(
                [("domain", ASCENDING), ("business_name", ASCENDING)], unique=True
            ),
        ]

    @classmethod
    def get_query(
        cls,
        user_id: uuid.UUID = None,
        business_name: str = None,
        is_deleted: bool = False,
        type: str = None,
        *args,
        **kwargs
    ) -> FindMany:
        query = super().get_query(user_id, business_name, is_deleted, *args, **kwargs)
        if type:
            query = query.find(cls.type == type)
        return query
