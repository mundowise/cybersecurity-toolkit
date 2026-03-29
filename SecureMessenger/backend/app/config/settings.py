# app/config/settings.py
from __future__ import annotations
import os
from typing import List, Set

def _split_csv(name: str, default: str = "") -> List[str]:
    raw = os.getenv(name, default) or ""
    items = [x.strip() for x in raw.split(",") if x.strip()]
    return items

def _split_csv_int(name: str, default: str = "") -> Set[int]:
    vals = set()
    for x in _split_csv(name, default):
        try:
            vals.add(int(x))
        except ValueError:
            continue
    return vals

class Settings:
    # JWT / seguridad
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE-THIS-IN-PRODUCTION")
    JWT_ALG: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_TTL_MIN: int = int(os.getenv("ACCESS_TOKEN_TTL_MIN", "15"))

    # CORS (lista de orígenes permitidos, separados por coma)
    CORS_ORIGINS: List[str] = _split_csv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000"
    )

    # Subidas
    FILE_MAX_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_MB", "25"))
    ALLOWED_EXTS: List[str] = _split_csv("ALLOWED_EXTS", "sm1")

    # Admins
    ADMIN_USER_IDS: Set[int] = _split_csv_int("ADMIN_USER_IDS", "")

settings = Settings()
