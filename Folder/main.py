# main.py

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import httpx

from database import engine, SessionLocal, Base
import models  # this imports your model classes

# 1️⃣ Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 2️⃣ DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "Mental Health Tracker is live!"}

from fastapi import HTTPException, status
from schemas import UserCreate, UserRead, MoodCreate, MoodRead, JournalCreate, JournalRead
import models
from database import SessionLocal, engine
from sqlalchemy.orm import Session

# make sure Base.metadata.create_all(...) already ran

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── Register User ────────────────────────────────────────────
@app.post("/users/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # check if username/email exists
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    db_user = models.User(
        username=user.username,
        email=user.email,
        password=user.password  # remember: hash this for production!
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ── List Users (for testing) ─────────────────────────────────
@app.get("/users/", response_model=list[UserRead])
def read_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


from fastapi import Depends

# ── Create Mood Entry ───────────────────────────────────────
@app.post("/users/{user_id}/moods/", response_model=MoodRead, status_code=201)
def add_mood_entry(
    user_id: int,
    mood: MoodCreate,
    db: Session = Depends(get_db)
):
    # verify user exists
    if not db.get(models.User, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    db_mood = models.MoodEntry(
        user_id=user_id,
        score=mood.score,
        category=mood.category
    )
    db.add(db_mood)
    db.commit()
    db.refresh(db_mood)
    return db_mood

# ── List Mood Entries ───────────────────────────────────────
@app.get("/users/{user_id}/moods/", response_model=list[MoodRead])
def list_mood_entries(
    user_id: int,
    db: Session = Depends(get_db)
):
    return db.query(models.MoodEntry).filter_by(user_id=user_id).all()

# ── Create Journal Entry ────────────────────────────────────
@app.post("/users/{user_id}/journals/", response_model=JournalRead, status_code=201)
def add_journal_entry(
    user_id: int,
    journal: JournalCreate,
    db: Session = Depends(get_db)
):
    if not db.get(models.User, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    db_journal = models.JournalEntry(
        user_id=user_id,
        content=journal.content
    )
    db.add(db_journal)
    db.commit()
    db.refresh(db_journal)
    return db_journal

# ── List Journal Entries ────────────────────────────────────
@app.get("/users/{user_id}/journals/", response_model=list[JournalRead])
def list_journal_entries(
    user_id: int,
    db: Session = Depends(get_db)
):
    return db.query(models.JournalEntry).filter_by(user_id=user_id).all()


# main.py (additions marked with ▶️)

from fastapi.security import OAuth2PasswordRequestForm
from auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
)
from schemas import Token
from datetime import timedelta
from database import SessionLocal

# ▶️ Token endpoint
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    user = authenticate_user(db, form_data.username, form_data.password)
    db.close()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

# ▶️ Protect user routes: use current_user dependency
@app.post("/users/", response_model=UserRead, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # leave open so new users can register
    ...

# Change to:
@app.get("/users/me", response_model=UserRead)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# ▶️ Protect mood and journal endpoints:
@app.post("/users/{user_id}/moods/", response_model=MoodRead, status_code=201)
def add_mood_entry(
    user_id: int,
    mood: MoodCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    ...
