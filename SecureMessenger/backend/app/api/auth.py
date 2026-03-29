from fastapi import APIRouter, HTTPException
from app.models.user import UserCreate, UserOut
from app.utils.security import hash_password, verify_password, create_jwt_token
from app.db import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut)
async def register_user(user: UserCreate):
    async with get_db() as db:
        cur = await db.execute("SELECT id FROM users WHERE alias = ?", (user.alias.strip(),))
        if await cur.fetchone():
            raise HTTPException(status_code=409, detail="Alias already exists")
        hashed = hash_password(user.password)
        cur = await db.execute(
            "INSERT INTO users (alias, hashed_password) VALUES (?, ?)",
            (user.alias.strip(), hashed)
        )
        await db.commit()
        return UserOut(id=cur.lastrowid, alias=user.alias.strip())

@router.post("/login")
async def login(user: UserCreate):
    async with get_db() as db:
        cur = await db.execute("SELECT id, hashed_password FROM users WHERE alias = ?", (user.alias.strip(),))
        row = await cur.fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        user_id, hashed = row
        if not verify_password(user.password, hashed):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_jwt_token({"sub": str(user_id)})
        return {"access_token": token, "token_type": "bearer", "user": {"id": user_id, "alias": user.alias.strip()}}

