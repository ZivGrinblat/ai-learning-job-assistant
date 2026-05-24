from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="AI Learning & Job Assistant",
    description="A backend API for text analysis, learning support, and job assistance.",
    version="0.1.0",
)

app.include_router(router)
