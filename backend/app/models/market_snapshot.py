from sqlalchemy import Column, Integer, String, Date, DateTime, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class MarketSnapshot(Base):
    """
    行情快照表
    每笔交易入场/出场时自动抓取，用于后续策略挖掘和模式分析
    """
    __tablename__ = "market_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(Integer, ForeignKey("trades.id"), nullable=False, index=True)
    snapshot_date = Column(Date, nullable=False, comment="快照日期")
    snapshot_type = Column(String(10), nullable=False, comment="entry=入场日 exit=出场日")
    symbol = Column(String(20), nullable=False, comment="标的代码")

    # ── 大盘数据 ──────────────────────────────────────
    sh_pct = Column(Float, nullable=True, comment="上证涨跌幅%")
    sz_pct = Column(Float, nullable=True, comment="深证涨跌幅%")
    cy_pct = Column(Float, nullable=True, comment="创业板涨跌幅%")
    sh_volume_ratio = Column(Float, nullable=True, comment="上证量能比（今日量/5日均量）")
    market_trend = Column(String(20), default="", comment="大盘趋势判断: up/down/sideways")

    # ── 个股数据 ──────────────────────────────────────
    stock_pct = Column(Float, nullable=True, comment="个股当日涨跌幅%")
    stock_volume = Column(Float, nullable=True, comment="个股成交量（万手）")
    stock_volume_ratio = Column(Float, nullable=True, comment="个股量能比")
    stock_turnover = Column(Float, nullable=True, comment="换手率%")
    stock_close = Column(Float, nullable=True, comment="收盘价")

    # ── 均线状态 ──────────────────────────────────────
    ma5 = Column(Float, nullable=True, comment="5日均线")
    ma10 = Column(Float, nullable=True, comment="10日均线")
    ma20 = Column(Float, nullable=True, comment="20日均线")
    # above_ma5/ma10/ma20: 1=股价在均线上方 0=下方
    above_ma5 = Column(Integer, nullable=True)
    above_ma10 = Column(Integer, nullable=True)
    above_ma20 = Column(Integer, nullable=True)
    # 均线多头排列: ma5>ma10>ma20=1
    ma_bullish = Column(Integer, nullable=True, comment="均线多头排列")

    # ── MACD ──────────────────────────────────────────
    macd_diff = Column(Float, nullable=True, comment="MACD DIF")
    macd_dea = Column(Float, nullable=True, comment="MACD DEA")
    macd_bar = Column(Float, nullable=True, comment="MACD 柱")
    macd_golden_cross = Column(Integer, nullable=True, comment="MACD金叉=1 死叉=-1 无=0")

    # ── 板块数据 ──────────────────────────────────────
    sector_name = Column(String(50), default="", comment="所属板块名称")
    sector_pct = Column(Float, nullable=True, comment="板块当日涨跌幅%")
    sector_rank = Column(Integer, nullable=True, comment="板块涨幅排名")

    # ── 抓取状态 ──────────────────────────────────────
    fetch_status = Column(String(20), default="pending",
                          comment="pending=待抓取 done=成功 failed=失败")
    fetch_error = Column(String(200), default="", comment="失败原因")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<MarketSnapshot trade_id={self.trade_id} date={self.snapshot_date} type={self.snapshot_type}>"