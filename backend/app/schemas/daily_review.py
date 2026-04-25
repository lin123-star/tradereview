from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List, Any


class NewsItem(BaseModel):
    sector: str
    title: str
    source: str
    sentiment: str
    sentiment_label: str


class VsRow(BaseModel):
    """计划vs实际对比的一行"""
    plan: str = ""
    actual: str = ""


class DailyReviewCreate(BaseModel):
    date: date

    # 摘要
    pnl_amount: float = 0.0
    trade_count: int = 0
    win_count: int = 0
    loss_count: int = 0

    # 盘面梳理
    market_overview: str = ""
    plan_accuracy: str = ""
    market_style: str = ""
    market_split: str = ""
    style_desc: str = ""
    leading_sectors: str = ""
    lagging_sectors: str = ""
    sector_summary: str = ""

    # 产业信息
    selected_sectors: List[str] = []
    extra_keywords: str = ""
    ai_news_result: List[Any] = []
    industry_summary: str = ""

    # 操作复盘
    vs_rows: List[VsRow] = []
    best_trade: str = ""
    worst_trade: str = ""
    emotion_state: str = ""
    key_lesson: str = ""
    counterfactual: str = ""
    next_hypothesis: str = ""
    luck_ratio: str = ""


class DailyReviewUpdate(DailyReviewCreate):
    date: Optional[date] = None


class DailyReviewOut(DailyReviewCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AISearchRequest(BaseModel):
    sectors: List[str] = Field(..., description="关注的板块列表")
    extra_keywords: str = Field("", description="补充关键词")
    review_date: date = Field(..., description="复盘日期")


class AISearchResponse(BaseModel):
    news: List[NewsItem]
    summary: str


class ArticleGenerateRequest(BaseModel):
    review_date: date
    frameworks: List[str] = ["resonance", "methodology", "reflection"]


class ArticleOut(BaseModel):
    id: int
    review_date: date
    framework: str
    title: str
    content: str
    word_count: int
    published: int
    created_at: datetime

    class Config:
        from_attributes = True
