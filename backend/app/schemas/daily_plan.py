from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List


class WatchItem(BaseModel):
    """观察池中的单个标的"""
    symbol: str = ""
    name: str = ""
    price: Optional[float] = None
    entry_condition: str = ""
    stop_loss: Optional[float] = None
    target: Optional[float] = None
    note: str = ""


class DailyPlanCreate(BaseModel):
    date: date

    # 大盘研判
    market_trend: str = ""
    market_sentiment: str = ""
    focus_sectors: List[str] = []
    market_analysis: str = ""

    # 操作纪律
    max_loss_limit: str = ""
    max_trade_count: int = 2
    emotion_weakness: str = ""

    # 观察池
    watchlist: List[WatchItem] = []

    # 入场计划
    entry_plan: str = ""
    core_hypothesis: str = ""


class DailyPlanUpdate(DailyPlanCreate):
    date: Optional[date] = None


class DailyPlanOut(DailyPlanCreate):
    id: int
    locked: bool
    created_at: datetime
    updated_at: datetime
    locked_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DailyPlanLockRequest(BaseModel):
    date: date