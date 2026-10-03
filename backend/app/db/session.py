from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import settings
from pathlib import Path

DATABASE_URL = settings.database_url
# Hosting providers hand out postgres:// or postgresql:// URLs; this app uses the psycopg 3 driver.
for _prefix in ("postgres://", "postgresql://"):
    if DATABASE_URL.startswith(_prefix):
        DATABASE_URL = "postgresql+psycopg://" + DATABASE_URL[len(_prefix):]

if settings.database_url.startswith("sqlite") and ":memory:" not in settings.database_url:
    database_path = settings.database_url.removeprefix("sqlite:///")
    Path(database_path).parent.mkdir(parents=True, exist_ok=True)
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
