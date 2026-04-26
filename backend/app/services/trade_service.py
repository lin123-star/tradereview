import logging
import asyncio
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.trade import Trade
from app.schemas.trade import TradeStep1, TradeStep2, TradeQuery

logger = logging.getLogger(__name__)


class TradeService:

    @staticmethod
    async def create(db: AsyncSession, data: TradeStep1) -> Trade:
        """Step1：创建交易记录，入场信息锁定，后台触发行情快照"""
        trade = Trade(
            symbol=data.symbol.upper().strip(),
            name=data.name,
            direction=data.direction,
            entry_price=data.entry_price,
            entry_time=data.entry_time,
            position_ratio=data.position_ratio,
            entry_logic=data.entry_logic,
            entry_locked=True,
            market_env=data.market_env,
            strategy=data.strategy,
            emotion=data.emotion,
            review_date=data.review_date,
            status="open",
            review_status="pending",
        )
        db.add(trade)
        await db.commit()
        await db.refresh(trade)
        logger.info(f"创建交易记录: {trade.symbol} {trade.direction} @ {trade.entry_price}")

        # 后台异步触发入场快照（不阻塞主流程）
        asyncio.create_task(
            TradeService._trigger_entry_snapshot(trade.id)
        )
        return trade

    @staticmethod
    async def _trigger_entry_snapshot(trade_id: int):
        try:
            from app.core.database import AsyncSessionLocal
            from app.services.snapshot_service import SnapshotService
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(Trade).where(Trade.id == trade_id))
                trade = result.scalar_one_or_none()
                if trade:
                    await SnapshotService.create_entry_snapshot(db, trade)
        except Exception as e:
            logger.error(f"入场快照后台任务失败: {e}")

    @staticmethod
    async def complete(db: AsyncSession, trade_id: int, data: TradeStep2) -> Trade:
        """Step2：填写出场信息，计算盈亏，触发出场快照"""
        trade = await TradeService.get_by_id(db, trade_id)
        if not trade:
            raise ValueError(f"交易记录 {trade_id} 不存在")
        if trade.status == "closed":
            raise ValueError(f"交易 {trade_id} 已出场，不能重复填写")

        trade.exit_price = data.exit_price
        trade.exit_time = data.exit_time
        trade.exit_logic = data.exit_logic
        trade.exit_emotion = data.exit_emotion
        trade.plan_followed = data.plan_followed
        trade.lesson = data.lesson
        trade.counterfactual = data.counterfactual
        trade.hypothesis = data.hypothesis
        trade.uncertainty = data.uncertainty
        trade.status = "closed"
        trade.pnl_amount, trade.pnl_ratio = TradeService._calc_pnl(trade)

        logger.info(f"完成交易: {trade.symbol} 盈亏={trade.pnl_amount:.2f}元")
        await db.commit()
        await db.refresh(trade)

        # 后台异步触发出场快照
        asyncio.create_task(
            TradeService._trigger_exit_snapshot(trade.id)
        )
        return trade

    @staticmethod
    async def _trigger_exit_snapshot(trade_id: int):
        try:
            from app.core.database import AsyncSessionLocal
            from app.services.snapshot_service import SnapshotService
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(Trade).where(Trade.id == trade_id))
                trade = result.scalar_one_or_none()
                if trade:
                    await SnapshotService.create_exit_snapshot(db, trade)
        except Exception as e:
            logger.error(f"出场快照后台任务失败: {e}")

    @staticmethod
    async def update_review_status(
        db: AsyncSession, trade_id: int, review_status: str
    ) -> Trade:
        trade = await TradeService.get_by_id(db, trade_id)
        if not trade:
            raise ValueError(f"交易记录 {trade_id} 不存在")
        trade.review_status = review_status
        await db.commit()
        await db.refresh(trade)
        return trade

    @staticmethod
    async def get_by_id(db: AsyncSession, trade_id: int) -> Optional[Trade]:
        result = await db.execute(select(Trade).where(Trade.id == trade_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(db: AsyncSession, query: TradeQuery) -> tuple[list[Trade], int]:
        conditions = []
        if query.status:
            conditions.append(Trade.status == query.status)
        if query.review_status:
            conditions.append(Trade.review_status == query.review_status)
        if query.symbol:
            conditions.append(Trade.symbol == query.symbol.upper())
        if query.start_date:
            conditions.append(Trade.entry_time >= query.start_date)
        if query.end_date:
            end_dt = datetime.combine(query.end_date, datetime.max.time())
            conditions.append(Trade.entry_time <= end_dt)

        base_q = select(Trade)
        if conditions:
            base_q = base_q.where(and_(*conditions))

        count_q = select(func.count()).select_from(base_q.subquery())
        total = (await db.execute(count_q)).scalar()

        result = await db.execute(
            base_q.order_by(Trade.entry_time.desc())
            .offset(query.offset)
            .limit(query.limit)
        )
        return list(result.scalars().all()), total

    @staticmethod
    async def get_pending_review(db: AsyncSession) -> list[Trade]:
        result = await db.execute(
            select(Trade)
            .where(Trade.status == "closed", Trade.review_status == "pending")
            .order_by(Trade.exit_time.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def delete(db: AsyncSession, trade_id: int) -> bool:
        trade = await TradeService.get_by_id(db, trade_id)
        if not trade:
            return False
        if trade.status == "closed":
            raise ValueError("已出场的交易记录不允许删除")
        await db.delete(trade)
        await db.commit()
        return True

    @staticmethod
    def _calc_pnl(trade: Trade) -> tuple[float, float]:
        if not trade.exit_price or not trade.entry_price:
            return 0.0, 0.0
        if trade.direction in ("buy", "add"):
            pnl_ratio = (trade.exit_price - trade.entry_price) / trade.entry_price
        else:
            pnl_ratio = (trade.entry_price - trade.exit_price) / trade.entry_price
        pnl_amount = trade.position_ratio * 100000 * pnl_ratio
        return round(pnl_amount, 2), round(pnl_ratio, 4)