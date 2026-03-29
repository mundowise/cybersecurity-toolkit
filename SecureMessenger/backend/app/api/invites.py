# app/api/invites.py
from __future__ import annotations
import base64, os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.db import get_db
from app.utils.security import get_current_user_id

router = APIRouter(prefix="/invites", tags=["invites"])

def _now():
    return datetime.now(timezone.utc)

def _b64url(n: int = 16) -> str:
    return base64.urlsafe_b64encode(os.urandom(n)).rstrip(b"=").decode()

class InviteCreateIn(BaseModel):
    ttl_minutes: int = 15
    is_group: bool = False
    name: str | None = None
    creator_pubkey: str  # base64 (X25519)

@router.post("/create")
async def create_invite(body: InviteCreateIn, request: Request):
    user_id = get_current_user_id(request)
    code = _b64url(16)  # 128 bits
    created = _now()
    expires = created + timedelta(minutes=max(1, min(body.ttl_minutes, 1440)))

    async with get_db() as db:
        # Crea chat SIEMPRE (1:1 o grupo)
        cur = await db.execute("INSERT INTO chats (is_group, name) VALUES (?, ?)", (int(body.is_group), body.name))
        await db.commit()
        chat_id = cur.lastrowid
        # Miembro creador
        await db.execute("INSERT OR IGNORE INTO chat_members (chat_id, user_id, role) VALUES (?, ?, 'owner')",
                         (chat_id, user_id))
        # Registra pubkey del creador para ECDH
        await db.execute(
            "INSERT OR REPLACE INTO chat_keys (chat_id, user_id, pubkey) VALUES (?, ?, ?)",
            (chat_id, user_id, body.creator_pubkey)
        )
        # Guarda invitación
        max_uses = 1 if not body.is_group else 1000000
        await db.execute(
            "INSERT INTO invites (code, creator_user_id, chat_id, is_group, max_uses, uses, created_at, expires_at) "
            "VALUES (?, ?, ?, ?, ?, 0, ?, ?)",
            (code, user_id, chat_id, int(body.is_group), max_uses, created.isoformat(), expires.isoformat())
        )
        await db.commit()

    return {
        "code": code,
        "expires_at": expires.isoformat(),
        "is_group": body.is_group,
        "chat_id": chat_id,
        "uri": f"sm://join?code={code}",
    }

class InviteRedeemIn(BaseModel):
    code: str
    redeemer_pubkey: str  # base64 (X25519)

@router.post("/redeem")
async def redeem_invite(body: InviteRedeemIn, request: Request):
    user_id = get_current_user_id(request)
    code = body.code.strip()

    async with get_db() as db:
        cur = await db.execute(
            "SELECT code, creator_user_id, chat_id, is_group, max_uses, uses, expires_at FROM invites WHERE code = ?",
            (code,)
        )
        row = await cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="not found")
        creator_id, chat_id, is_group, max_uses, uses, expires_at = row[1], row[2], int(row[3]), int(row[4]), int(row[5]), row[6]
        # exp
        if expires_at and expires_at < _now().isoformat():
            raise HTTPException(status_code=404, detail="not found")
        if uses >= max_uses:
            raise HTTPException(status_code=404, detail="not found")
        if not is_group and user_id == creator_id:
            raise HTTPException(status_code=400, detail="cannot redeem own invite")

        # Une al canjeador
        await db.execute(
            "INSERT OR IGNORE INTO chat_members (chat_id, user_id, role) VALUES (?, ?, 'member')",
            (chat_id, user_id)
        )
        # Registra pubkey del canjeador
        await db.execute(
            "INSERT OR REPLACE INTO chat_keys (chat_id, user_id, pubkey) VALUES (?, ?, ?)",
            (chat_id, user_id, body.redeemer_pubkey)
        )

        # Sube contador y consume (si 1:1 dejamos uses=1)
        uses += 1
        await db.execute(
            "UPDATE invites SET uses = ? WHERE code = ?",
            (uses, code)
        )

        # Obtén pubkey del creador para devolvérsela al canjeador
        curk = await db.execute("SELECT pubkey FROM chat_keys WHERE chat_id=? AND user_id=?", (chat_id, creator_id))
        rowk = await curk.fetchone()
        other_pub = rowk[0] if rowk else None
        await db.commit()

    return {"chat_id": chat_id, "other_pubkey": other_pub}
