from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class Strategy(Base):
    """
    用户自定义策略标签表
    每个策略是一个可复用的交易规则模板
    """
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, comment="策略名称，如：均线金叉+量能放大")

    # ── 策略描述 ──────────────────────────────────────
    category = Column(String(30), default="", comment="大类：trend/reversal/news/quant/other")
    description = Column(Text, default="", comment="策略简介")

    # ── 具体条件 ──────────────────────────────────────
    entry_signal = Column(Text, default="", comment="入场信号描述")
    stop_loss_rule = Column(Text, default="", comment="止损规则描述")
    take_profit_rule = Column(Text, default="", comment="止盈/目标位规则描述")
    applicable_market = Column(String(50), default="", comment="适用市场环境")

    # ── 统计数据（定期更新） ──────────────────────────
    total_count = Column(Integer, default=0, comment="总使用次数")
    win_count = Column(Integer, default=0, comment="盈利次数")
    loss_count = Column(Integer, default=0, comment="亏损次数")
    win_rate = Column(Float, default=0.0, comment="胜率")
    avg_pnl_ratio = Column(Float, default=0.0, comment="平均盈亏比")
    avg_win_ratio = Column(Float, default=0.0, comment="平均盈利幅度")
    avg_loss_ratio = Column(Float, default=0.0, comment="平均亏损幅度")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Strategy name={self.name} win_rate={self.win_rate}>"