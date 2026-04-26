from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class SocraticSession(Base):
    """
    AI苏格拉底审讯会话表
    每笔交易对应一个审讯会话
    """
    __tablename__ = "socratic_sessions"

    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(Integer, ForeignKey("trades.id"), nullable=False, index=True)

    # 对话历史：[{"role": "ai"|"user", "content": "..."}]
    messages = Column(JSON, default=list, comment="完整对话历史")

    # AI识别的认知盲区列表：["事后止损", "忽略大盘", ...]
    blind_spots = Column(JSON, default=list, comment="识别出的认知盲区")

    # 审讯总结
    summary = Column(Text, default="", comment="审讯结束后的总结")

    # 状态: active=进行中 completed=已完成
    status = Column(String(20), default="active")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<SocraticSession trade_id={self.trade_id} status={self.status}>"
