# schemas.py

from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class JournalCreate(BaseModel):
    content: str

class JournalRead(BaseModel):
    id: int
    content: str
    timestamp: datetime
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class MoodCreate(BaseModel):
    score: int
    category: str

class MoodRead(BaseModel):
    id: int
    score: int
    category: str
    timestamp: datetime
    user_id: int

    model_config = ConfigDict(from_attributes=True)
