from __future__ import annotations
import os, uuid
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import FileResponse

from app.db import get_db
from app.utils.security import get_current_user_id
from app.config.settings import settings

VOICE_DIR = "voice"
os.makedirs(VOICE_DIR, exist_ok=True)

router = APIRouter(prefix="/voice", tags=["voice"])

def _ensure_sm1_and_size(data: bytes):
    if len(data) > settings.FILE_MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail="file too large")
    if len(data) < 3 + 24 + 16:
        raise HTTPException(status_code=400, detail="invalid sm1 size")
    if not (data[0] == 0x53 and data[1] == 0x4D and data[2] == 0x31):
        raise HTTPException(status_code=400, detail="invalid sm1 magic")

async def _user_is_member(db, chat_id: int, user_id: int) -> bool:
    cur = await db.execute(
        "SELECT 1 FROM chat_members WHERE chat_id=? AND user_id=? LIMIT 1",
        (chat_id, user_id),
    )
    return (await cur.fetchone()) is not None

async def _resolve_voice_path_if_authorized(voice_id: str, user_id: int) -> Optional[str]:
    async with get_db() as db:
        cur = await db.execute(
            "SELECT chat_id FROM messages WHERE type='voice' AND content=? LIMIT 1",
            (voice_id,),
        )
        row = await cur.fetchone()
        if not row:
            return None
        chat_id = row[0]
        if not await _user_is_member(db, chat_id, user_id):
            return None

    path = os.path.join(VOICE_DIR, f"{voice_id}.sm1")
    if not os.path.exists(path):
        return None
    return path

@router.post("/upload")
async def upload_voice(
    request: Request,
    chat_id: int = Form(...),
    filename: Optional[str] = Form(None),
    mimetype: Optional[str] = Form("audio/opus+sm1"),
    file: UploadFile = File(...),
):
    user_id = get_current_user_id(request)

    # Exige membresía al chat destino
    async with get_db() as db:
        if not await _user_is_member(db, chat_id, user_id):
            raise HTTPException(status_code=404, detail="not found")

    data = await file.read()
    _ensure_sm1_and_size(data)

    vid = uuid.uuid4().hex
    out_path = os.path.join(VOICE_DIR, f"{vid}.sm1")
    with open(out_path, "wb") as f:
        f.write(data)

    return {
        "voice_id": vid,
        "filename": filename or f"{vid}.sm1",
        "mimetype": mimetype or "audio/opus+sm1",
    }

@router.get("/download/{voice_id}")
async def download_voice(voice_id: str, request: Request):
    user_id = get_current_user_id(request)
    path = await _resolve_voice_path_if_authorized(voice_id, user_id)
    if not path:
        raise HTTPException(status_code=404, detail="not found")

    return FileResponse(
        path,
        media_type="audio/opus+sm1",
        filename=os.path.basename(path),
    )
