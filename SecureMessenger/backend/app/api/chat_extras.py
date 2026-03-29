# app/api/chat_extras.py
from __future__ import annotations
import hashlib, os
from typing import List

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.db import get_db
from app.utils.security import get_current_user_id

UPLOAD_DIR = "uploads"
VOICE_DIR = "voice"

router = APIRouter(prefix="/chat", tags=["chat"])

async def _ensure_member(db, chat_id: int, user_id: int):
    cur = await db.execute("SELECT 1 FROM chat_members WHERE chat_id=? AND user_id=? LIMIT 1", (chat_id, user_id))
    if await cur.fetchone() is None:
        raise HTTPException(status_code=403, detail="forbidden")

def _fingerprint_hex(chat_id: int, created_at: str, members: List[int]) -> str:
    s = f"chat:{chat_id}:{created_at}:{','.join(map(str, sorted(members)))}"
    h = hashlib.sha256(s.encode()).hexdigest()
    return "-".join([h[i:i+2] for i in range(0, 20, 2)]).upper()

class AliasIn(BaseModel):
    chat_id: int
    display_name: str

@router.post("/alias")
async def set_alias(body: AliasIn, request: Request):
    user_id = get_current_user_id(request)
    dn = body.display_name.strip()
    if len(dn) > 64:
        raise HTTPException(status_code=400, detail="alias too long")
    async with get_db() as db:
        await _ensure_member(db, body.chat_id, user_id)
        await db.execute("UPDATE chat_members SET display_name=? WHERE chat_id=? AND user_id=?",
                         (dn or None, body.chat_id, user_id))
        await db.commit()
    return {"ok": True}

@router.get("/fingerprint/{chat_id}")
async def chat_fingerprint(chat_id: int, request: Request):
    user_id = get_current_user_id(request)
    async with get_db() as db:
        await _ensure_member(db, chat_id, user_id)
        cur = await db.execute("SELECT created_at FROM chats WHERE id=?", (chat_id,))
        row = await cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="not found")
        created_at = row[0]
        curm = await db.execute("SELECT user_id FROM chat_members WHERE chat_id=?", (chat_id,))
        members = [r[0] async for r in curm]
    fp = _fingerprint_hex(chat_id, created_at, members)
    return {"chat_id": chat_id, "fingerprint": fp}

@router.get("/meta/{chat_id}")
async def chat_meta(chat_id: int, request: Request):
    user_id = get_current_user_id(request)
    async with get_db() as db:
        await _ensure_member(db, chat_id, user_id)
        cur = await db.execute("SELECT id, is_group, name, created_at FROM chats WHERE id=?", (chat_id,))
        row = await cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="not found")
        _, is_group, name, created_at = row
        curm = await db.execute("SELECT user_id, display_name, role FROM chat_members WHERE chat_id=?", (chat_id,))
        members = [{"user_id": r[0], "display_name": r[1], "role": r[2]} async for r in curm]
    fp = _fingerprint_hex(chat_id, created_at, [m["user_id"] for m in members])
    return {"id": chat_id, "is_group": bool(is_group), "name": name, "created_at": created_at,
            "members": members, "fingerprint": fp}

@router.get("/keyinfo/{chat_id}")
async def keyinfo(chat_id: int, request: Request):
    """Devuelve pubkeys por miembro para que el cliente derive la clave (ECDH)."""
    user_id = get_current_user_id(request)
    async with get_db() as db:
        await _ensure_member(db, chat_id, user_id)
        cur = await db.execute("SELECT user_id, pubkey FROM chat_keys WHERE chat_id=?", (chat_id,))
        items = [{"user_id": r[0], "pubkey": r[1]} async for r in cur]
    return {"chat_id": chat_id, "keys": items}

@router.post("/clear/{chat_id}")
async def clear_chat(chat_id: int, request: Request):
    user_id = get_current_user_id(request)
    deleted_files = 0
    deleted_voices = 0
    async with get_db() as db:
        await _ensure_member(db, chat_id, user_id)
        curf = await db.execute("SELECT content FROM messages WHERE chat_id=? AND type='file'", (chat_id,))
        file_ids = [r[0] async for r in curf]
        curv = await db.execute("SELECT content FROM messages WHERE chat_id=? AND type='voice'", (chat_id,))
        voice_ids = [r[0] async for r in curv]

        for fid in file_ids:
            try:
                os.remove(os.path.join(UPLOAD_DIR, f"{fid}.sm1")); deleted_files += 1
            except FileNotFoundError:
                pass
        for vid in voice_ids:
            try:
                os.remove(os.path.join(VOICE_DIR, f"{vid}.sm1")); deleted_voices += 1
            except FileNotFoundError:
                pass

        await db.execute("DELETE FROM messages WHERE chat_id=?", (chat_id,))
        await db.commit()
    return {"status": "ok", "deleted_messages": "all", "files_removed": deleted_files, "voices_removed": deleted_voices}
