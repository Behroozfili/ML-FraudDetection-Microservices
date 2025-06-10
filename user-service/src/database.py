# user-service/src/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database settings
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/userdb"
)

# For the development environment, SQLite can be used
if os.getenv("ENVIRONMENT") == "development":
    DATABASE_URL = "sqlite:///./users.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Dependency to get a database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()