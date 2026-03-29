from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatCreate(BaseModel):
    is_group: bool = False
    name: Optional[str] = None
    members: List[int]  # user_ids

class ChatOut(BaseModel):
    id: int
    is_group: bool
    name: Optional[str]
    members: List[int]

class MessageCreate(BaseModel):
    chat_id: int
    content: Optional[str] = None        # ciphertext base64 o file/voice id
    expires_at: Optional[datetime] = None
    type: str = "text"                   # 'text'|'file'|'voice'|'system'
    filename: Optional[str] = None
    mimetype: Optional[str] = None

class MessageOut(BaseModel):
    id: int
    chat_id: int
    sender_id: int
    content: Optional[str]
    sent_at: str
    expires_at: Optional[str]
    type: str
    filename: Optional[str]
    mimetype: Optional[str]
