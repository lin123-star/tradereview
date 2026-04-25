from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Float, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class Trade(Base):
    """
    交易记录表
    两步录入：
      Step1 盘中填（入场后锁定）：symbol/direction/entry_*/position_ratio/entry_logic
      Step2 收盘后填：exit_*/emotion/strategy/plan_followed/lesson 等
    """
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)

    # ── Step1：入场信息（提交后锁定）────────────────
    symbol = Column(String(20), nullable=False, comment="标的代码，如 600519")
    name = Column(String(50), default="", comment="标的名称，如 贵州茅台")
    direction = Column(String(10), nullable=False, comment="buy/sell/add/reduce")
    entry_price = Column(Float, nullable=False, comment="入场价格")
    entry_time = Column(DateTime(timezone=True), nullable=False, comment="入场时间")
    position_ratio = Column(Float, default=0.0, comment="仓位比例 0-1")
    entry_logic = Column(Text, nullable=False, comment="入场逻辑（锁定不可修改）")
    entry_locked = Column(Boolean, default=True, comment="入场信息是否已锁定")

    # ── Step2：出场信息（收盘后填）──────────────────
    exit_price = Column(Float, nullable=True, comment="出场价格，持仓中为null")
    exit_time = Column(DateTime(timezone=True), nullable=True, comment="出场时间")
    exit_logic = Column(Text, default="", comment="出场逻辑")

    # ── 盈亏（自动计算）─────────────────────────────
    pnl_amount = Column(Float, nullable=True, comment="盈亏金额（元），出场后计算")
    pnl_ratio = Column(Float, nullable=True, comment="盈亏比例，出场后计算")

    # ── 交易标签 ─────────────────────────────────────
    emotion = Column(String(20), default="", comment="入场情绪: calm/greedy/panic/hesitant/impulsive")
    exit_emotion = Column(String(20), default="", comment="出场情绪")
    strategy = Column(String(50), default="", comment="策略标签: trend/reversal/news/quant/other")
    market_env = Column(String(30), default="", comment="市场环境: bull/bear/sideways/volatile")
    plan_followed = Column(String(10), default="", comment="是否符合计划: yes/no/partial")

    # ── 复盘字段 ─────────────────────────────────────
    lesson = Column(Text, default="", comment="核心教训（一句话）")
    counterfactual = Column(Text, default="", comment="如果重来会怎么做")
    hypothesis = Column(Text, default="", comment="下次相同情境的可验证假设")
    uncertainty = Column(Integer, default=3, comment="不确定性评分 1-5，5=纯运气")

    # ── 关联 ─────────────────────────────────────────
    review_date = Column(Date, nullable=True, comment="关联的每日复盘日期")

    # ── 状态 ─────────────────────────────────────────
    status = Column(String(10), default="open", comment="open=持仓中 closed=已出场")
    review_status = Column(String(10), default="pending",
                           comment="pending=待复盘 reviewing=审讯中 done=已完成")

    # ── 元数据 ───────────────────────────────────────
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Trade {self.symbol} {self.direction} {self.entry_price} [{self.status}]>"
