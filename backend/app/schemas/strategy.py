from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class StrategyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="策略名称")
    category: str = Field("", description="大类: trend/reversal/news/quant/other")
    description: str = ""
    entry_signal: str = ""
    stop_loss_rule: str = ""
    take_profit_rule: str = ""
    applicable_market: str = ""


class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    entry_signal: Optional[str] = None
    stop_loss_rule: Optional[str] = None
    take_profit_rule: Optional[str] = None
    applicable_market: Optional[str] = None


class StrategyOut(StrategyCreate):
    id: int
    total_count: int
    win_count: int
    loss_count: int
    win_rate: float
    avg_pnl_ratio: float
    avg_win_ratio: float
    avg_loss_ratio: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True