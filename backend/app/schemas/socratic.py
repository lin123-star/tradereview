from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class Message(BaseModel):
    role: str       # "ai" | "user"
    content: str


class SessionOut(BaseModel):
    id: int
    trade_id: int
    messages: List[Message]
    blind_spots: List[str]
    summary: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StartSessionRequest(BaseModel):
    trade_id: int


class ReplyRequest(BaseModel):
    session_id: int
    user_message: str


class ReplyResponse(BaseModel):
    session_id: int
    ai_message: str
    blind_spots: List[str]
    status: str          # active | completed
    summary: str         # 审讯完成时才有内容
