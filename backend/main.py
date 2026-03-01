from fastapi import FastAPI
from app.routes import auth

app = FastAPI(
    title="AI Internship Recommendation API",
    version="1.0.0"
)

# Include auth router
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

@app.get("/")
def read_root():
    return {"message": "AI Internship Recommendation System Backend Running"}

@app.get("/health/")
def health_check():
    return {"status": "ok"}