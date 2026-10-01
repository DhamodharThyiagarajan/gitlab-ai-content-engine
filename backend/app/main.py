from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from app.config import settings
from app.db.session import Base, engine
from app.api import auth, content_jobs, reviews, publishing, metrics

Base.metadata.create_all(bind=engine)
# create_all does not alter tables created by earlier versions of the application.
user_columns = {column["name"] for column in inspect(engine).get_columns("users")}
if "firebase_uid" not in user_columns:
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE users ADD COLUMN firebase_uid VARCHAR(128)"))
        connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_firebase_uid ON users (firebase_uid)"))
if "password_hash" in user_columns:
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE users DROP COLUMN password_hash"))
app=FastAPI(title=settings.app_name,version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in settings.cors_origins.split(",")],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.include_router(auth.router,prefix="/api")
app.include_router(content_jobs.router,prefix="/api")
app.include_router(content_jobs.jobs_router,prefix="/api")
app.include_router(reviews.router,prefix="/api")
app.include_router(publishing.router,prefix="/api")
app.include_router(metrics.router,prefix="/api")
@app.get("/health")
def health(): return {"status":"ok","service":settings.app_name}
