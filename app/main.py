import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import speaking, auth
from app.services.telegram_bot import start_bot

app = FastAPI(
    title="IELTS Speaking Practice API",
    description="API for admin management and IELTS speaking practice questions",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Productionda frontend URLni kiriting
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(speaking.router)
app.include_router(auth.router)

# Start the Telegram bot when the app starts
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_bot())