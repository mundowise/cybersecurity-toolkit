from fastapi import APIRouter, HTTPException, Request
from typing import List
from app.models.chat import ChatCreate, ChatOut, MessageCreate, MessageOut
from app.db import get_db
from app.utils.security import get_current_user_id

router = APIRouter(prefix="/chat", tags=["chat"])

async def _ensure_member(db, chat_id: int, user_id: int):
    cur = await db.execute(
        "SELECT 1 FROM chat_members WHERE chat_id = ? AND user_id = ?",
        (chat_id, user_id)
    )
    if await cur.fetchone() is None:
        raise HTTPException(status_code=403, detail="not a chat member")

@router.get("/list", response_model=List[ChatOut])
async def list_chats(request: Request):
    user_id = get_current_user_id(request)
    async with get_db() as db:
        cur = await db.execute("""
            SELECT c.id, c.is_group, c.name
            FROM chats c
            JOIN chat_members m ON m.chat_id = c.id
            WHERE m.user_id = ?
            ORDER BY c.id ASC
        """, (user_id,))
        chats = []
        for cid, is_group, name in await cur.fetchall():
            curm = await db.execute("SELECT user_id FROM chat_members WHERE chat_id = ?", (cid,))
            members = [r[0] async for r in curm]
            chats.append(ChatOut(id=cid, is_group=bool(is_group), name=name, members=members))
        return chats

@router.post("/create", response_model=ChatOut)
async def create_chat(body: ChatCreate, request: Request):
    user_id = get_current_user_id(request)
    async with get_db() as db:
        cur = await db.execute("INSERT INTO chats (is_group, name) VALUES (?, ?)", (int(body.is_group), body.name))
        await db.commit()
        chat_id = cur.lastrowid
        # add creator
        await db.execute("INSERT OR IGNORE INTO chat_members (chat_id, user_id, role) VALUES (?, ?, 'owner')", (chat_id, user_id))
        # add members (sin duplicar)
        uniq = {uid for uid in body.members if isinstance(uid, int)}
        uniq.discard(user_id)
        for uid in uniq:
            await db.execute("INSERT OR IGNORE INTO chat_members (chat_id, user_id, role) VALUES (?, ?, 'member')", (chat_id, uid))
        await db.commit()
        curm = await db.execute("SELECT user_id FROM chat_members WHERE chat_id = ?", (chat_id,))
        members = [r[0] async for r in curm]
        return ChatOut(id=chat_id, is_group=body.is_group, name=body.name, members=members)

@router.get("/messages/{chat_id}", response_model=List[MessageOut])
async def get_messages(chat_id: int, request: Request):
    user_id = get_current_user_id(request)
    async with get_db() as db:
        await _ensure_member(db, chat_id, user_id)
        cur = await db.execute(
            "SELECT id, chat_id, sender_id, content, sent_at, expires_at, type, filename, mimetype "
            "FROM messages WHERE chat_id = ? ORDER BY sent_at ASC",
            (chat_id,)
        )
        rows = await cur.fetchall()
        return [
            MessageOut(
                id=r[0], chat_id=r[1], sender_id=r[2], content=r[3],
                sent_at=r[4], expires_at=r[5], type=r[6],
                filename=r[7], mimetype=r[8]
            ) for r in rows
        ]

@router.post("/message/send", response_model=MessageOut)
async def send_message(msg: MessageCreate, request: Request):
    user_id = get_current_user_id(request)
    async with get_db() as db:
        await _ensure_member(db, msg.chat_id, user_id)
        if msg.type == "text" and not (msg.content and msg.content.strip()):
            raise HTTPException(status_code=400, detail="ciphertext required")
        cur = await db.execute(
            "INSERT INTO messages (chat_id, sender_id, content, expires_at, type, filename, mimetype) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (msg.chat_id, user_id, msg.content, msg.expires_at.isoformat() if msg.expires_at else None,
             msg.type, msg.filename, msg.mimetype)
        )
        await db.commit()
        mid = cur.lastrowid
        cur2 = await db.execute(
            "SELECT id, chat_id, sender_id, content, sent_at, expires_at, type, filename, mimetype "
            "FROM messages WHERE id = ?", (mid,)
        )
        r = await cur2.fetchone()
        return MessageOut(
            id=r[0], chat_id=r[1], sender_id=r[2], content=r[3],
            sent_at=r[4], expires_at=r[5], type=r[6], filename=r[7], mimetype=r[8]
        )
