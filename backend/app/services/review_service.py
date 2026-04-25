from datetime import date
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.daily_review import DailyReview, GeneratedArticle
from app.schemas.daily_review import DailyReviewCreate, DailyReviewUpdate


class DailyReviewService:

    @staticmethod
    async def get_by_date(db: AsyncSession, review_date: date) -> Optional[DailyReview]:
        result = await db.execute(
            select(DailyReview).where(DailyReview.date == review_date)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(db: AsyncSession, limit: int = 30) -> list[DailyReview]:
        result = await db.execute(
            select(DailyReview).order_by(DailyReview.date.desc()).limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def upsert(
        db: AsyncSession,
        review_date: date,
        data: DailyReviewCreate | DailyReviewUpdate,
    ) -> DailyReview:
        """有则更新，无则创建（按日期唯一）"""
        review = await DailyReviewService.get_by_date(db, review_date)

        if review is None:
            review = DailyReview(date=review_date)
            db.add(review)

        payload = data.model_dump(exclude_none=True, exclude={"date"})
        for key, value in payload.items():
            setattr(review, key, value)

        await db.commit()
        await db.refresh(review)
        return review

    @staticmethod
    async def save_articles(
        db: AsyncSession,
        review_date: date,
        articles: list[dict],
    ) -> list[GeneratedArticle]:
        saved = []
        for art in articles:
            # 同一日期+框架只保留最新一篇
            result = await db.execute(
                select(GeneratedArticle).where(
                    GeneratedArticle.review_date == review_date,
                    GeneratedArticle.framework == art["framework"],
                )
            )
            existing = result.scalar_one_or_none()
            if existing:
                existing.title = art["title"]
                existing.content = art["content"]
                existing.word_count = len(art["content"])
                saved.append(existing)
            else:
                obj = GeneratedArticle(
                    review_date=review_date,
                    framework=art["framework"],
                    title=art["title"],
                    content=art["content"],
                    word_count=len(art["content"]),
                )
                db.add(obj)
                saved.append(obj)

        await db.commit()
        for obj in saved:
            await db.refresh(obj)
        return saved

    @staticmethod
    async def get_articles(
        db: AsyncSession, review_date: date
    ) -> list[GeneratedArticle]:
        result = await db.execute(
            select(GeneratedArticle)
            .where(GeneratedArticle.review_date == review_date)
            .order_by(GeneratedArticle.created_at.desc())
        )
        return result.scalars().all()
