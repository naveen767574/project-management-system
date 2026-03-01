# backend/app/main.py

from fastapi import FastAPI
from app.routes.auth import router as auth_router
from app.routes.health import router as health_router
from app.database import Base, engine

app = FastAPI(title="AI Internship Recommendation API", version="1.0.0")

# Create database tables
Base.metadata.create_all(bind=engine)

app.include_router(health_router)
app.include_router(auth_router)


@app.get("/")
def root():
    return {"message": "Backend running successfully!"}