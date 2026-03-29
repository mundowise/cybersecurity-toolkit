import os
from datetime import datetime, timezone
from app.db import get_db

UPLOAD_DIR = "uploads"
VOICE_DIR = "voice"

def _now_iso():
    return datetime.now(timezone.utc).isoformat()

async def cleanup_all():
    deleted_files, deleted_voices = 0, 0
    now = _now_iso()
    async with get_db() as db:
        # FILES expirados
        cur = await db.execute("SELECT DISTINCT content FROM messages WHERE type='file' AND expires_at IS NOT NULL AND expires_at < ?", (now,))
        for (fid,) in await cur.fetchall():
            try:
                os.remove(os.path.join(UPLOAD_DIR, f"{fid}.sm1"))
                deleted_files += 1
            except FileNotFoundError:
                pass
        await db.execute("DELETE FROM messages WHERE type='file' AND expires_at IS NOT NULL AND expires_at < ?", (now,))

        # VOICE expirados
        cur = await db.execute("SELECT DISTINCT content FROM messages WHERE type='voice' AND expires_at IS NOT NULL AND expires_at < ?", (now,))
        for (vid,) in await cur.fetchall():
            try:
                os.remove(os.path.join(VOICE_DIR, f"{vid}.sm1"))
                deleted_voices += 1
            except FileNotFoundError:
                pass
        await db.execute("DELETE FROM messages WHERE type='voice' AND expires_at IS NOT NULL AND expires_at < ?", (now,))
        await db.commit()
    return {"files_removed": deleted_files, "voices_removed": deleted_voices}
