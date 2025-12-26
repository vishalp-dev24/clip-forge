from fastapi import FastAPI
from api.routes import router as api_router
from utils.logger import setup_logging

setup_logging()

app = FastAPI(title="ClipForge Backend - Whisper Pipeline")

app.include_router(api_router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
