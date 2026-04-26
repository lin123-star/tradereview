from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Float, Boolean, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class DailyPlan(Base):
    """
    每日交易计划表
    盘前填写，提交后锁定不可修改
    """
    __tablename__ = "daily_plans"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, nullable=False, index=True, comment="计划日期")
    locked = Column(Boolean, default=False, comment="是否已锁定")

    # ── 大盘研判 ──────────────────────────────────────
    market_trend = Column(String(30), default="", comment="大盘趋势: bull/mild_bull/sideways/mild_bear/bear")
    market_sentiment = Column(String(30), default="", comment="市场情绪: optimistic/mild_optimistic/neutral/pessimistic/panic")
    focus_sectors = Column(JSON, default=list, comment="重点关注板块列表")
    market_analysis = Column(Text, default="", comment="大盘分析（支撑/压力/逻辑）")

    # ── 操作纪律 ──────────────────────────────────────
    max_loss_limit = Column(String(20), default="", comment="最大亏损上限，如 -1.5%")
    max_trade_count = Column(Integer, default=2, comment="最多操作笔数")
    emotion_weakness = Column(String(50), default="", comment="今日重点克服的情绪弱点")

    # ── 观察池 ────────────────────────────────────────
    # [{"symbol": "600519", "name": "贵州茅台", "price": 1748.5,
    #   "entry_condition": "突破1750", "stop_loss": 1700, "target": 1800, "note": ""}]
    watchlist = Column(JSON, default=list, comment="今日观察标的列表")

    # ── 入场计划 ──────────────────────────────────────
    entry_plan = Column(Text, default="", comment="具体入场条件/止损/目标位描述")
    core_hypothesis = Column(Text, default="", comment="今日核心可验证假设")

    # ── 元数据 ────────────────────────────────────────
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    locked_at = Column(DateTime(timezone=True), nullable=True, comment="锁定时间")

    def __repr__(self):
        return f"<DailyPlan date={self.date} locked={self.locked}>"