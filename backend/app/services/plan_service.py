import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.daily_plan import DailyPlan
from app.schemas.daily_plan import DailyPlanCreate, DailyPlanUpdate
from datetime import date

logger = logging.getLogger(__name__)


class PlanService:

    @staticmethod
    async def get_by_date(db: AsyncSession, plan_date: date) -> Optional[DailyPlan]:
        result = await db.execute(
            select(DailyPlan).where(DailyPlan.date == plan_date)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(db: AsyncSession, limit: int = 30) -> list[DailyPlan]:
        result = await db.execute(
            select(DailyPlan).order_by(DailyPlan.date.desc()).limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def upsert(
        db: AsyncSession,
        plan_date: date,
        data: DailyPlanCreate | DailyPlanUpdate,
    ) -> DailyPlan:
        """有则更新，无则创建，锁定后拒绝修改"""
        plan = await PlanService.get_by_date(db, plan_date)

        if plan is None:
            plan = DailyPlan(date=plan_date, locked=False)
            db.add(plan)
        elif plan.locked:
            raise ValueError(f"{plan_date} 的计划已锁定，不允许修改")

        payload = data.model_dump(exclude_none=True, exclude={"date"})
        for key, value in payload.items():
            setattr(plan, key, value)

        await db.commit()
        await db.refresh(plan)
        logger.info(f"计划已保存: date={plan_date}")
        return plan

    @staticmethod
    async def lock(db: AsyncSession, plan_date: date) -> DailyPlan:
        """锁定计划，锁定后不可修改"""
        plan = await PlanService.get_by_date(db, plan_date)
        if not plan:
            raise ValueError(f"{plan_date} 的计划不存在，请先保存")
        if plan.locked:
            raise ValueError(f"{plan_date} 的计划已经锁定")

        plan.locked = True
        plan.locked_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(plan)
        logger.info(f"计划已锁定: date={plan_date} locked_at={plan.locked_at}")
        return plan