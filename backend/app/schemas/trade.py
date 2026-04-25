from pydantic import BaseModel, Field, model_validator
from datetime import date, datetime
from typing import Optional


# ── Step1：入场录入 ───────────────────────────────────
class TradeStep1(BaseModel):
    """盘中填写，提交后锁定"""
    symbol: str = Field(..., description="标的代码")
    name: str = Field("", description="标的名称")
    direction: str = Field(..., description="buy/sell/add/reduce")
    entry_price: float = Field(..., gt=0, description="入场价格")
    entry_time: datetime = Field(..., description="入场时间")
    position_ratio: float = Field(0.0, ge=0, le=1, description="仓位比例 0-1")
    entry_logic: str = Field(..., min_length=1, description="入场逻辑，必填")
    market_env: str = Field("", description="市场环境")
    strategy: str = Field("", description="策略标签")
    emotion: str = Field("", description="入场情绪")
    review_date: Optional[date] = Field(None, description="关联复盘日期")


# ── Step2：出场录入 ───────────────────────────────────
class TradeStep2(BaseModel):
    """收盘后填写"""
    exit_price: float = Field(..., gt=0, description="出场价格")
    exit_time: datetime = Field(..., description="出场时间")
    exit_logic: str = Field("", description="出场逻辑")
    exit_emotion: str = Field("", description="出场情绪")
    plan_followed: str = Field("", description="yes/no/partial")
    lesson: str = Field("", description="核心教训")
    counterfactual: str = Field("", description="反事实思考")
    hypothesis: str = Field("", description="下次可验证假设")
    uncertainty: int = Field(3, ge=1, le=5, description="不确定性评分1-5")


# ── 响应体 ────────────────────────────────────────────
class TradeOut(BaseModel):
    id: int
    symbol: str
    name: str
    direction: str
    entry_price: float
    entry_time: datetime
    position_ratio: float
    entry_logic: str
    entry_locked: bool
    exit_price: Optional[float]
    exit_time: Optional[datetime]
    exit_logic: str
    pnl_amount: Optional[float]
    pnl_ratio: Optional[float]
    emotion: str
    exit_emotion: str
    strategy: str
    market_env: str
    plan_followed: str
    lesson: str
    counterfactual: str
    hypothesis: str
    uncertainty: int
    review_date: Optional[date]
    status: str
    review_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── 列表查询参数 ──────────────────────────────────────
class TradeQuery(BaseModel):
    status: Optional[str] = None          # open/closed
    review_status: Optional[str] = None   # pending/done
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    symbol: Optional[str] = None
    limit: int = Field(50, le=200)
    offset: int = 0
