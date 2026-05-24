from fastapi import FastAPI

app = FastAPI(
    title="AI Learning & Job Assistant",
    description="A backend API for text analysis, learning support, and job assistance.",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}