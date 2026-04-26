import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.strategy import StrategyCreate, StrategyUpdate, StrategyOut
from app.services.strategy_service import StrategyService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/strategy", tags=["策略管理"])


@router.get("", response_model=list[StrategyOut])
async def get_all(db: AsyncSession = Depends(get_db)):
    """获取所有自定义策略（按使用次数降序）"""
    return await StrategyService.get_all(db)


@router.post("", response_model=StrategyOut)
async def create(data: StrategyCreate, db: AsyncSession = Depends(get_db)):
    """创建新策略"""
    try:
        return await StrategyService.create(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{strategy_id}", response_model=StrategyOut)
async def update(
    strategy_id: int,
    data: StrategyUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新策略信息"""
    try:
        return await StrategyService.update(db, strategy_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{strategy_id}")
async def delete(strategy_id: int, db: AsyncSession = Depends(get_db)):
    """删除策略（有关联交易时禁止删除）"""
    try:
        ok = await StrategyService.delete(db, strategy_id)
        if not ok:
            raise HTTPException(status_code=404, detail="策略不存在")
        return {"detail": "已删除"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{strategy_id}/recalc", response_model=StrategyOut)
async def recalc_stats(strategy_id: int, db: AsyncSession = Depends(get_db)):
    """手动重新计算策略统计数据"""
    try:
        return await StrategyService.recalc_stats(db, strategy_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/recalc-all")
async def recalc_all(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """后台重新计算所有策略统计"""
    background_tasks.add_task(StrategyService.recalc_all, db)
    return {"detail": "统计重算任务已启动"}