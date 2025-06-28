
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./mental_health.db"

# 1️⃣ Create engine
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# 2️⃣ Create Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 3️⃣ Base class for models
Base = declarative_base()
