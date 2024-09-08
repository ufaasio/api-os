import uuid

from apps.base.models import BaseEntity, BusinessEntity, OwnedEntity
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from .schemas import AppDomainSchema, AuthorizedDomainSchema


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


class Extension(OwnedEntity):
    name: str
    domain: str
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
    permissions: list[uuid.UUID] = []

    @classmethod
    def create_exclude_set(cls) -> list[str]:
        return super().create_exclude_set() + ["is_active"]

    class Settings:
        indexes = [
            IndexModel([("name", ASCENDING)], unique=True),
            IndexModel([("domain", ASCENDING)], unique=True),
        ]


class Installed(BusinessEntity):
    extension_id: uuid.UUID
    is_active: bool = False
    permissions: list[Permission] = []

    class Settings:
        indexes = [
            IndexModel(
                [("extension_id", ASCENDING), ("app_id", ASCENDING)], unique=True
            ),
        ]
