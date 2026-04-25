import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.trade import TradeStep1, TradeStep2, TradeOut, TradeQuery
from app.services.trade_service import TradeService
from typing import Optional
from datetime import date

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/trade", tags=["交易记录"])


# ── Step1：入场录入 ───────────────────────────────────
@router.post("", response_model=TradeOut, summary="Step1 入场录入（提交后锁定）")
async def create_trade(data: TradeStep1, db: AsyncSession = Depends(get_db)):
    try:
        return await TradeService.create(db, data)
    except Exception as e:
        logger.error(f"创建交易失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ── Step2：出场录入 ───────────────────────────────────
@router.post("/{trade_id}/complete", response_model=TradeOut, summary="Step2 出场录入")
async def complete_trade(
    trade_id: int,
    data: TradeStep2,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await TradeService.complete(db, trade_id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"完成交易失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── 查询 ──────────────────────────────────────────────
@router.get("", response_model=dict, summary="查询交易列表")
async def list_trades(
    status: Optional[str] = Query(None, description="open/closed"),
    review_status: Optional[str] = Query(None, description="pending/reviewing/done"),
    symbol: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    query = TradeQuery(
        status=status,
        review_status=review_status,
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )
    trades, total = await TradeService.get_list(db, query)
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "items": [TradeOut.model_validate(t) for t in trades],
    }


@router.get("/pending-review", response_model=list[TradeOut], summary="待复盘的已出场交易")
async def get_pending_review(db: AsyncSession = Depends(get_db)):
    trades = await TradeService.get_pending_review(db)
    return trades


@router.get("/{trade_id}", response_model=TradeOut, summary="查询单条交易")
async def get_trade(trade_id: int, db: AsyncSession = Depends(get_db)):
    trade = await TradeService.get_by_id(db, trade_id)
    if not trade:
        raise HTTPException(status_code=404, detail="交易记录不存在")
    return trade


# ── 更新审讯状态 ──────────────────────────────────────
@router.patch("/{trade_id}/review-status", response_model=TradeOut)
async def update_review_status(
    trade_id: int,
    review_status: str = Query(..., description="pending/reviewing/done"),
    db: AsyncSession = Depends(get_db),
):
    valid = {"pending", "reviewing", "done"}
    if review_status not in valid:
        raise HTTPException(status_code=400, detail=f"review_status 必须是 {valid}")
    try:
        return await TradeService.update_review_status(db, trade_id, review_status)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ── 删除 ──────────────────────────────────────────────
@router.delete("/{trade_id}", summary="删除交易（仅限持仓中）")
async def delete_trade(trade_id: int, db: AsyncSession = Depends(get_db)):
    try:
        ok = await TradeService.delete(db, trade_id)
        if not ok:
            raise HTTPException(status_code=404, detail="交易记录不存在")
        return {"detail": "已删除"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
