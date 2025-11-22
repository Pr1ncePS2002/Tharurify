# app/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Any

class UserCreate(BaseModel):
    username: str
    email: EmailStr # Use EmailStr for basic email validation
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class ChatCreate(BaseModel):
    user_id: int
    question: str
    answer: str

class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None
    meta: Any | None = None

# You might add more schemas for your other routes (speech, resume) as needed
