import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.trade import Trade
from app.schemas.trade import TradeStep1, TradeStep2, TradeQuery

logger = logging.getLogger(__name__)


class TradeService:

    @staticmethod
    async def create(db: AsyncSession, data: TradeStep1) -> Trade:
        """Step1：创建交易记录，入场信息锁定"""
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
        return trade

    @staticmethod
    async def complete(db: AsyncSession, trade_id: int, data: TradeStep2) -> Trade:
        """Step2：填写出场信息，计算盈亏"""
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

        # 计算盈亏
        trade.pnl_amount, trade.pnl_ratio = TradeService._calc_pnl(trade)
        logger.info(f"完成交易: {trade.symbol} 盈亏={trade.pnl_amount:.2f}元 {trade.pnl_ratio:.2%}")

        await db.commit()
        await db.refresh(trade)
        return trade

    @staticmethod
    async def update_review_status(
        db: AsyncSession, trade_id: int, review_status: str
    ) -> Trade:
        """更新审讯状态: pending / reviewing / done"""
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
        """查询交易列表，返回 (列表, 总数)"""
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
            # 包含 end_date 当天
            from datetime import timedelta
            end_dt = datetime.combine(query.end_date, datetime.max.time())
            conditions.append(Trade.entry_time <= end_dt)

        base_q = select(Trade)
        if conditions:
            base_q = base_q.where(and_(*conditions))

        # 总数
        from sqlalchemy import func
        count_q = select(func.count()).select_from(base_q.subquery())
        total = (await db.execute(count_q)).scalar()

        # 分页
        result = await db.execute(
            base_q.order_by(Trade.entry_time.desc())
            .offset(query.offset)
            .limit(query.limit)
        )
        trades = result.scalars().all()
        return list(trades), total

    @staticmethod
    async def get_pending_review(db: AsyncSession) -> list[Trade]:
        """获取所有待复盘的已出场交易"""
        result = await db.execute(
            select(Trade)
            .where(Trade.status == "closed", Trade.review_status == "pending")
            .order_by(Trade.exit_time.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def delete(db: AsyncSession, trade_id: int) -> bool:
        """删除交易记录（仅允许删除 open 状态）"""
        trade = await TradeService.get_by_id(db, trade_id)
        if not trade:
            return False
        if trade.status == "closed":
            raise ValueError("已出场的交易记录不允许删除，请联系管理员")
        await db.delete(trade)
        await db.commit()
        logger.info(f"删除交易记录: id={trade_id}")
        return True

    @staticmethod
    def _calc_pnl(trade: Trade) -> tuple[float, float]:
        """计算盈亏金额和比例"""
        if not trade.exit_price or not trade.entry_price:
            return 0.0, 0.0

        if trade.direction in ("buy", "add"):
            pnl_ratio = (trade.exit_price - trade.entry_price) / trade.entry_price
        else:
            # sell/reduce：空头逻辑
            pnl_ratio = (trade.entry_price - trade.exit_price) / trade.entry_price

        # 简化盈亏金额：用仓位比例 * 10万基准仓计算，实际使用时可接入真实资金
        base_amount = trade.position_ratio * 100000
        pnl_amount = base_amount * pnl_ratio

        return round(pnl_amount, 2), round(pnl_ratio, 4)
