import uuid
from enum import Enum

from fastapi_mongo_base.schemas import BaseEntitySchema
from pydantic import BaseModel


class AppDomainSchema(BaseModel):
    homepage: str | None = None
    terms_of_service: str | None = None
    privacy_policy: str | None = None


class AuthorizedDomainSchema(BaseModel):
    authorized_redirect_uris: list[str] = []
    authorized_origins: list[str] = []

    @property
    def authorized_domains(self):
        from urllib.parse import urlparse

        return list(
            set(
                urlparse(uri).netloc
                for uri in self.authorized_redirect_uris + self.authorized_origins
            )
        )


class AppType(str, Enum):
    basic = "basic"
    ipg = "ipg"


class AppSchema(BaseEntitySchema):
    name: str
    domain: str
    type: AppType = AppType.basic

    # @field_validator
    # def validate_domain(cls, domain: str):
    #     if not domain.startswith("http"):
    #         domain = f"https://{domain}"
    #     return domain


class PermissionSchema(BaseEntitySchema):
    business_id: uuid.UUID
    third_party_app_id: uuid.UUID
    can_submit_proposal: bool
