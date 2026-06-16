"""
Application entry point.

Wires FastAPI, CORS, API routes, DB init on startup, and static frontend.
Mount StaticFiles last — otherwise it steals paths like /health and /notes.
"""

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.services.note_store import init_db

load_dotenv()

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app = FastAPI(
    title="AI Learning & Job Assistant",
    description="A backend API for text analysis, learning support, and job assistance.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.on_event("startup")
def on_startup() -> None:
    """Ensure SQLite exists before any request hits note endpoints."""
    init_db()


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
