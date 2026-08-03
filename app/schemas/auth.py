from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    username: str
    role: str
    student_id: str | None


class TokenResponse(UserResponse):
    access_token: str
    token_type: str = "bearer"
