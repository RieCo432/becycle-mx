from uuid import UUID

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class UserTokenData(BaseModel):
    username: str | None = None


class ClientTokenData(BaseModel):
    client_id: UUID | None = None
