from fastapi import FastAPI
from app.routes import speaking

app = FastAPI(
    title="IELTS Speaking Practice API",
    description="API for fetching random IELTS speaking practice questions",
    version="1.0.0"
)

app.include_router(speaking.router)