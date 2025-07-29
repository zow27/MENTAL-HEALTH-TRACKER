

from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

import models, schemas
from database import get_db

# ---------- security settings ----------
SECRET_KEY = "your-secret-key-here"        # <-- generate a strong one!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# ---------- password hashing ----------
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ---------- user CRUD ----------
def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_pw = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ---------- authentication ----------
def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user(db, token_data.username)
    if user is None:
        raise credentials_exception
    return user


# ---------- journal & mood helpers ----------
def create_journal(db: Session, user_id: int, journal: schemas.JournalCreate):
    db_j = models.Journal(content=journal.content, user_id=user_id)
    db.add(db_j)
    db.commit()
    db.refresh(db_j)
    return db_j

def get_journals(db: Session, user_id: int):
    return db.query(models.Journal).filter(models.Journal.user_id == user_id).order_by(models.Journal.timestamp.desc()).all()

def create_mood(db: Session, user_id: int, mood: schemas.MoodCreate):
    db_m = models.Mood(score=mood.score, category=mood.category, user_id=user_id)
    db.add(db_m)
    db.commit()
    db.refresh(db_m)
    return db_m

def get_moods(db: Session, user_id: int):
    return db.query(models.Mood).filter(models.Mood.user_id == user_id).order_by(models.Mood.timestamp.desc()).all()


def get_password_hash(password: str) -> str:
    try:
        return pwd_context.hash(password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not hash password: {str(e)}")
