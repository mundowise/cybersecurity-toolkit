from __future__ import annotations
import os, uuid
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import FileResponse

from app.db import get_db
from app.utils.security import get_current_user_id
from app.config.settings import settings

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/files", tags=["files"])

def _ensure_sm1_and_size(data: bytes):
    if len(data) > settings.FILE_MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail="file too large")
    if len(data) < 3 + 24 + 16:
        # 3 bytes "SM1" + 24 nonce + 16 tag
        raise HTTPException(status_code=400, detail="invalid sm1 size")
    if not (data[0] == 0x53 and data[1] == 0x4D and data[2] == 0x31):  # "SM1"
        raise HTTPException(status_code=400, detail="invalid sm1 magic")

async def _user_is_member(db, chat_id: int, user_id: int) -> bool:
    cur = await db.execute(
        "SELECT 1 FROM chat_members WHERE chat_id=? AND user_id=? LIMIT 1",
        (chat_id, user_id),
    )
    return (await cur.fetchone()) is not None

async def _resolve_blob_path_if_authorized(file_id: str, user_id: int) -> Optional[str]:
    """
    Política anti-oráculo: devolvemos None (que el caller traduce a 404)
    **tanto** si no hay referencia (mensajes borrados/expirados),
    como si no es miembro, o si el fichero no existe.
    """
    async with get_db() as db:
        # 1) Encuentra un chat que referencie ese file_id
        cur = await db.execute(
            "SELECT chat_id FROM messages WHERE type='file' AND content=? LIMIT 1",
            (file_id,),
        )
        row = await cur.fetchone()
        if not row:
            return None
        chat_id = row[0]

        # 2) ¿Usuario es miembro?
        if not await _user_is_member(db, chat_id, user_id):
            return None

    # 3) ¿Existe el blob en disco?
    path = os.path.join(UPLOAD_DIR, f"{file_id}.sm1")
    if not os.path.exists(path):
        return None

    return path

@router.post("/upload")
async def upload_file(
    request: Request,
    chat_id: int = Form(...),
    filename: Optional[str] = Form(None),
    mimetype: Optional[str] = Form("application/octet-stream+sm1"),
    file: UploadFile = File(...),
):
    """
    Sube **únicamente** blobs cifrados .sm1 y exige membresía en el chat.
    La asociación con el mensaje la hace el cliente con /chat/message/send (type='file', content=file_id).
    """
    user_id = get_current_user_id(request)

    # Verifica membresía ANTES de aceptar datos (evita "stuffing")
    async with get_db() as db:
        if not await _user_is_member(db, chat_id, user_id):
            # No reveles si el chat existe: usa 404 o 403; preferimos 404 para no filtrar
            raise HTTPException(status_code=404, detail="not found")

    data = await file.read()
    _ensure_sm1_and_size(data)

    fid = uuid.uuid4().hex
    out_path = os.path.join(UPLOAD_DIR, f"{fid}.sm1")
    with open(out_path, "wb") as f:
        f.write(data)

    return {
        "file_id": fid,
        "filename": filename or f"{fid}.sm1",
        "mimetype": mimetype or "application/octet-stream+sm1",
    }

@router.get("/download/{file_id}")
async def download_file(file_id: str, request: Request):
    """
    Devuelve 404 tanto si no existe como si el usuario no está autorizado.
    Evita canal lateral 403/404.
    """
    user_id = get_current_user_id(request)
    path = await _resolve_blob_path_if_authorized(file_id, user_id)
    if not path:
        raise HTTPException(status_code=404, detail="not found")

    return FileResponse(
        path,
        media_type="application/octet-stream+sm1",
        filename=os.path.basename(path),
    )
