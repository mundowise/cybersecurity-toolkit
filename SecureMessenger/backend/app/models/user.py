from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    alias: str
    password: str

class UserOut(BaseModel):
    id: int
    alias: str

class UserInDB(BaseModel):
    id: int
    alias: str
    hashed_password: str
