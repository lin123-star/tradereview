import logging
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.daily_review import (
    DailyReviewCreate, DailyReviewUpdate, DailyReviewOut,
    AISearchRequest, AISearchResponse, NewsItem,
    ArticleOut,
)
from app.services.review_service import DailyReviewService
from app.services.ai_service import search_industry_news, generate_articles

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/review", tags=["每日复盘"])


# !! 固定路径必须在动态路径 /{review_date} 之前注册，否则 FastAPI 会把
# "list" / "ai" 当成日期参数导致 404 或解析错误

# ── 固定路径 ──────────────────────────────────────────

@router.get("/list", response_model=list[DailyReviewOut])
async def get_review_list(limit: int = 30, db: AsyncSession = Depends(get_db)):
    return await DailyReviewService.get_list(db, limit)


@router.post("/ai/search-news", response_model=AISearchResponse)
async def ai_search_news(req: AISearchRequest):
    """调用 Gemini + Google Search 搜索今日产业动态"""
    try:
        result = await search_industry_news(
            sectors=req.sectors,
            extra_keywords=req.extra_keywords,
            review_date=req.review_date,
        )
        news = [NewsItem(**item) for item in result.get("news", [])]
        return AISearchResponse(news=news, summary=result.get("summary", ""))
    except Exception as e:
        logger.error(f"AI搜索失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── 动态路径 /{review_date} ───────────────────────────

@router.get("/{review_date}", response_model=DailyReviewOut)
async def get_review(review_date: date, db: AsyncSession = Depends(get_db)):
    review = await DailyReviewService.get_by_date(db, review_date)
    if not review:
        raise HTTPException(status_code=404, detail="当日复盘记录不存在")
    return review


@router.post("/{review_date}", response_model=DailyReviewOut)
async def upsert_review(
    review_date: date,
    data: DailyReviewCreate,
    db: AsyncSession = Depends(get_db),
):
    return await DailyReviewService.upsert(db, review_date, data)


@router.patch("/{review_date}", response_model=DailyReviewOut)
async def partial_update_review(
    review_date: date,
    data: DailyReviewUpdate,
    db: AsyncSession = Depends(get_db),
):
    review = await DailyReviewService.get_by_date(db, review_date)
    if not review:
        raise HTTPException(status_code=404, detail="当日复盘记录不存在，请先 POST 创建")
    return await DailyReviewService.upsert(db, review_date, data)


@router.post("/{review_date}/generate-articles", response_model=list[ArticleOut])
async def generate_review_articles(
    review_date: date,
    db: AsyncSession = Depends(get_db),
):
    review = await DailyReviewService.get_by_date(db, review_date)
    if not review:
        raise HTTPException(status_code=404, detail="请先保存复盘内容再生成文章")

    review_dict = {
        col.name: getattr(review, col.name)
        for col in review.__table__.columns
    }

    try:
        articles = await generate_articles(review_dict)
    except Exception as e:
        logger.error(f"文章生成失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    saved = await DailyReviewService.save_articles(db, review_date, articles)
    return saved


@router.get("/{review_date}/articles", response_model=list[ArticleOut])
async def get_review_articles(
    review_date: date,
    db: AsyncSession = Depends(get_db),
):
    return await DailyReviewService.get_articles(db, review_date)