from __future__ import annotations
import base64, os, time, uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from fastapi import HTTPException, status, Request
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config.settings import settings

# Argon2 para contraseñas
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def _secret_bytes() -> bytes:
    s = settings.SECRET_KEY
    if s.startswith("base64:"):
        return base64.b64decode(s.split("base64:",1)[1])
    return s.encode()

SECRET_BYTES = _secret_bytes()

def create_jwt_token(data: Dict[str, Any]) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        **data,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.ACCESS_TOKEN_TTL_MIN)).timestamp()),
        "jti": str(uuid.uuid4()),
        "iss": "secure-messenger",
        "aud": "secure-messenger-client",
    }
    return jwt.encode(payload, SECRET_BYTES, algorithm=settings.JWT_ALG)

def _decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, SECRET_BYTES, algorithms=[settings.JWT_ALG], audience="secure-messenger-client")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

# Lista negra simple en memoria (mejor Redis en prod)
_JTI_BLACKLIST: dict[str, float] = {}

def revoke_jti(jti: str, exp_ts: int) -> None:
    _JTI_BLACKLIST[jti] = float(exp_ts)

def jti_revoked(jti: str) -> bool:
    now = time.time()
    for k, v in list(_JTI_BLACKLIST.items()):
        if v < now:
            _JTI_BLACKLIST.pop(k, None)
    return jti in _JTI_BLACKLIST

def get_current_user_id(request: Request) -> int:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = auth.split(" ", 1)[1].strip()
    payload = _decode_token(token)
    if jti_revoked(payload.get("jti","")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Revoked token")
    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    try:
        return int(sub)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid subject in token")

def require_admin(user_id: int) -> None:
    if user_id not in settings.ADMIN_USER_IDS:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
