from pydantic import BaseModel


class UserToken(BaseModel):
    access_token: str
    token_type: str


class UserTokenData(BaseModel):
    username: str | None = None