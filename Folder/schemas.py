

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# ── USER ────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str  # in real life, hash this!

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True

# ── MOOD ENTRY ──────────────────────────────────────────────

class MoodCreate(BaseModel):
    score: float
    category: str

class MoodRead(BaseModel):
    id: int
    user_id: int
    timestamp: datetime
    score: float
    category: str

    class Config:
        orm_mode = True

# ── JOURNAL ENTRY ───────────────────────────────────────────

class JournalCreate(BaseModel):
    content: str

class JournalRead(BaseModel):
    id: int
    user_id: int
    timestamp: datetime
    content: str

    class Config:
        orm_mode = True


from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
