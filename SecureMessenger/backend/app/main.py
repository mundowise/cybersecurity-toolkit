# app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, auth, files, voice, cleanup
from app.api import invites
from app.api import chat_extras
from app.db import init_db
from app.config.settings import settings

def _cors_origins() -> list[str]:
    try:
        return settings.CORS_ORIGINS or ["http://localhost:3000", "http://127.0.0.1:3000"]
    except Exception:
        return ["http://localhost:3000", "http://127.0.0.1:3000"]

app = FastAPI(title="SecureMessenger Backend", version="1.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE","OPTIONS"],
    allow_headers=["Authorization","Content-Type"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(files.router)
app.include_router(voice.router)
app.include_router(cleanup.router)
app.include_router(invites.router)
app.include_router(chat_extras.router)

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.get("/health")
async def health():
    return {"ok": True}
