import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from datetime import date
from app.core.database import get_db
from app.services.snapshot_service import SnapshotService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/snapshot", tags=["行情快照"])


class SnapshotOut(BaseModel):
    id: int
    trade_id: int
    snapshot_date: date
    snapshot_type: str
    symbol: str
    sh_pct: Optional[float] = None
    sz_pct: Optional[float] = None
    cy_pct: Optional[float] = None
    sh_volume_ratio: Optional[float] = None
    market_trend: str = ""
    stock_pct: Optional[float] = None
    stock_volume: Optional[float] = None
    stock_volume_ratio: Optional[float] = None
    stock_turnover: Optional[float] = None
    stock_close: Optional[float] = None
    ma5: Optional[float] = None
    ma10: Optional[float] = None
    ma20: Optional[float] = None
    above_ma5: Optional[int] = None
    above_ma10: Optional[int] = None
    above_ma20: Optional[int] = None
    ma_bullish: Optional[int] = None
    macd_diff: Optional[float] = None
    macd_dea: Optional[float] = None
    macd_bar: Optional[float] = None
    macd_golden_cross: Optional[int] = None
    sector_name: str = ""
    sector_pct: Optional[float] = None
    sector_rank: Optional[int] = None
    fetch_status: str = ""
    fetch_error: str = ""

    class Config:
        from_attributes = True


@router.get("/trade/{trade_id}", response_model=list[SnapshotOut])
async def get_trade_snapshots(trade_id: int, db: AsyncSession = Depends(get_db)):
    """获取某笔交易的所有行情快照"""
    return await SnapshotService.get_by_trade(db, trade_id)


@router.post("/retry-failed", summary="重试所有失败的快照抓取")
async def retry_failed(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """手动触发重试所有失败的快照"""
    background_tasks.add_task(SnapshotService.retry_failed, db)
    return {"detail": "重试任务已启动，请稍后查看日志"}


@router.post("/manual/{trade_id}", summary="手动触发指定交易的快照抓取")
async def manual_fetch(
    trade_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """手动为指定交易触发行情快照抓取"""
    from sqlalchemy import select
    from app.models.trade import Trade
    result = await db.execute(select(Trade).where(Trade.id == trade_id))
    trade = result.scalar_one_or_none()
    if not trade:
        raise HTTPException(status_code=404, detail="交易记录不存在")

    background_tasks.add_task(SnapshotService.create_entry_snapshot, db, trade)
    if trade.status == "closed":
        background_tasks.add_task(SnapshotService.create_exit_snapshot, db, trade)

    return {"detail": f"快照抓取任务已启动: trade_id={trade_id}"}