

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
import requests

import models, schemas, auth
from database import engine, get_db
from typing import List
from reddit import reddit_router
app = FastAPI(
    title="Mental Health Tracker API",
    description="A simple API for journaling and mood tracking",
    version="1.0.0"
)

app.include_router(reddit_router)







models.Base.metadata.create_all(bind=engine)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ACCESS_TOKEN_EXPIRE_MINUTES = 30


@app.post(
    "/token",
    response_model=schemas.Token,
    tags=["Authentication"],
    summary="Login and get an access token"
)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post(
    "/users/",
    response_model=schemas.UserOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"],
    summary="Register a new user",
    responses={
        500: {
            "description": "Internal Server Error – Could not create user",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not hash password"}
                }
            },
        }
    },
)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if username already exists
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")

    # Check if email already exists
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    return auth.create_user(db=db, user=user)

@app.get(
    "/users/me",
    response_model=schemas.UserOut,
    tags=["Users"],
    summary="Get current logged-in user"
)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.get(
    "/users/all",
    response_model=List[schemas.UserOut],
    tags=["Users"],
    summary="List all users except yourself"
)
def get_all_users(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.User).filter(models.User.id != current_user.id).all()


def verify_user(user_id: int, current_user: models.User, allow_view: bool = False):
    if user_id != current_user.id:
        if allow_view:
            return  # allow viewing other users' data
        raise HTTPException(status_code=403, detail="Not authorized")

@app.post(
    "/users/{user_id}/journals/",
    response_model=schemas.JournalRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Journal"],
    summary="Add a journal entry"
)
def add_journal_entry(
    user_id: int,
    journal: schemas.JournalCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    verify_user(user_id, current_user)
    return auth.create_journal(db=db, user_id=user_id, journal=journal)

@app.get("/users/{user_id}/journals/")
def list_journal_entries(
    user_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    verify_user(user_id, current_user, allow_view=True)
    return auth.get_journals(db=db, user_id=user_id)


def list_journal_entries(
    user_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    verify_user(user_id, current_user)
    return auth.get_journals(db=db, user_id=user_id)




@app.post(
    "/users/{user_id}/moods/",
    response_model=schemas.MoodRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Mood"],
    summary="Record a mood entry"
)

def add_mood_entry(
    user_id: int,
    mood: schemas.MoodCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    verify_user(user_id, current_user, allow_view=True)
    return auth.create_mood(db=db, user_id=user_id, mood=mood)
    
    
@app.get(
    "/users/{user_id}/moods/")
def list_mood_entries(
    user_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    verify_user(user_id, current_user, allow_view=True)
    return auth.get_moods(db=db, user_id=user_id)

@app.get(
    "/users/{user_id}/moods/",
    response_model=List[schemas.MoodRead],
    tags=["Mood"],
    summary="List all mood entries for a user"
)
def list_mood_entries(
    user_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    verify_user(user_id, current_user)
    return auth.get_moods(db=db, user_id=user_id)



from pydantic import BaseModel, EmailStr, field_validator

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator('password')
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        return v



@app.get("/", tags=["Root"], summary="Health check")
def read_root():
    return {"message": "Mental Health Tracker API is up and running!"}
