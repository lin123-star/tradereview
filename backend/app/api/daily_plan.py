import logging
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.daily_plan import DailyPlanCreate, DailyPlanUpdate, DailyPlanOut
from app.services.plan_service import PlanService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/plan", tags=["每日计划"])


@router.get("/list", response_model=list[DailyPlanOut])
async def get_plan_list(limit: int = 30, db: AsyncSession = Depends(get_db)):
    return await PlanService.get_list(db, limit)


@router.get("/{plan_date}", response_model=DailyPlanOut)
async def get_plan(plan_date: date, db: AsyncSession = Depends(get_db)):
    plan = await PlanService.get_by_date(db, plan_date)
    if not plan:
        raise HTTPException(status_code=404, detail="当日计划不存在")
    return plan


@router.post("/{plan_date}", response_model=DailyPlanOut)
async def upsert_plan(
    plan_date: date,
    data: DailyPlanCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建或更新计划（锁定后拒绝）"""
    try:
        return await PlanService.upsert(db, plan_date, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{plan_date}/lock", response_model=DailyPlanOut)
async def lock_plan(plan_date: date, db: AsyncSession = Depends(get_db)):
    """锁定计划，锁定后不可修改"""
    try:
        return await PlanService.lock(db, plan_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))