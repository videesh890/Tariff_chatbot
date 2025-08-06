from fastapi import FastAPI
from .endpoints import router as api_router

app = FastAPI(
    title="Tariff Management Chatbot",
    description="API for AI-powered tariff management",
    version="0.1"
)
app.include_router(api_router)