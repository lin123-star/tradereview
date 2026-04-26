from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)

    # ── Step1 入场（锁定） ────────────────────────────
    symbol = Column(String(20), nullable=False)
    name = Column(String(50), default="")
    direction = Column(String(10), nullable=False)
    entry_price = Column(Float, nullable=False)
    entry_time = Column(DateTime(timezone=True), nullable=False)
    position_ratio = Column(Float, default=0.0)
    entry_logic = Column(Text, nullable=False)
    entry_locked = Column(Boolean, default=True)

    # ── Step2 出场 ────────────────────────────────────
    exit_price = Column(Float, nullable=True)
    exit_time = Column(DateTime(timezone=True), nullable=True)
    exit_logic = Column(Text, default="")
    pnl_amount = Column(Float, nullable=True)
    pnl_ratio = Column(Float, nullable=True)

    # ── 标签 ──────────────────────────────────────────
    emotion = Column(String(20), default="")
    exit_emotion = Column(String(20), default="")

    # 自定义策略外键
    strategy_tag_id = Column(
        Integer,
        ForeignKey("strategies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    # 保留旧字段兼容
    strategy = Column(String(50), default="")

    market_env = Column(String(30), default="")
    plan_followed = Column(String(10), default="")

    # ── 复盘 ──────────────────────────────────────────
    lesson = Column(Text, default="")
    counterfactual = Column(Text, default="")
    hypothesis = Column(Text, default="")
    uncertainty = Column(Integer, default=3)

    review_date = Column(Date, nullable=True)
    status = Column(String(10), default="open")
    review_status = Column(String(10), default="pending")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())