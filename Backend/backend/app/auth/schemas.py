from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    email: str
    password: str = Field(..., max_length=72)

