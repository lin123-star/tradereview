import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.strategy import Strategy
from app.models.trade import Trade
from app.schemas.strategy import StrategyCreate, StrategyUpdate

logger = logging.getLogger(__name__)


class StrategyService:

    @staticmethod
    async def get_all(db: AsyncSession) -> list[Strategy]:
        result = await db.execute(
            select(Strategy).order_by(Strategy.total_count.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, strategy_id: int) -> Optional[Strategy]:
        result = await db.execute(
            select(Strategy).where(Strategy.id == strategy_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Optional[Strategy]:
        result = await db.execute(
            select(Strategy).where(Strategy.name == name)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: StrategyCreate) -> Strategy:
        # 检查名称是否已存在
        existing = await StrategyService.get_by_name(db, data.name)
        if existing:
            raise ValueError(f"策略「{data.name}」已存在")

        strategy = Strategy(**data.model_dump())
        db.add(strategy)
        await db.commit()
        await db.refresh(strategy)
        logger.info(f"创建策略: {strategy.name}")
        return strategy

    @staticmethod
    async def update(
        db: AsyncSession, strategy_id: int, data: StrategyUpdate
    ) -> Strategy:
        strategy = await StrategyService.get_by_id(db, strategy_id)
        if not strategy:
            raise ValueError(f"策略 {strategy_id} 不存在")

        payload = data.model_dump(exclude_none=True)
        for key, val in payload.items():
            setattr(strategy, key, val)

        await db.commit()
        await db.refresh(strategy)
        return strategy

    @staticmethod
    async def delete(db: AsyncSession, strategy_id: int) -> bool:
        strategy = await StrategyService.get_by_id(db, strategy_id)
        if not strategy:
            return False
        if strategy.total_count > 0:
            raise ValueError(
                f"策略「{strategy.name}」已有 {strategy.total_count} 笔关联交易，不允许删除"
            )
        await db.delete(strategy)
        await db.commit()
        return True

    @staticmethod
    async def recalc_stats(db: AsyncSession, strategy_id: int) -> Strategy:
        """根据关联的交易记录重新计算策略统计数据"""
        strategy = await StrategyService.get_by_id(db, strategy_id)
        if not strategy:
            raise ValueError(f"策略 {strategy_id} 不存在")

        # 查询所有使用该策略的已出场交易
        result = await db.execute(
            select(Trade).where(
                Trade.strategy_tag_id == strategy_id,
                Trade.status == "closed",
            )
        )
        trades = result.scalars().all()

        if not trades:
            strategy.total_count = 0
            strategy.win_count = 0
            strategy.loss_count = 0
            strategy.win_rate = 0.0
            strategy.avg_pnl_ratio = 0.0
            strategy.avg_win_ratio = 0.0
            strategy.avg_loss_ratio = 0.0
        else:
            wins = [t for t in trades if (t.pnl_ratio or 0) > 0]
            losses = [t for t in trades if (t.pnl_ratio or 0) <= 0]

            strategy.total_count = len(trades)
            strategy.win_count = len(wins)
            strategy.loss_count = len(losses)
            strategy.win_rate = round(len(wins) / len(trades), 4)
            strategy.avg_pnl_ratio = round(
                sum(t.pnl_ratio or 0 for t in trades) / len(trades), 4
            )
            strategy.avg_win_ratio = round(
                sum(t.pnl_ratio or 0 for t in wins) / len(wins), 4
            ) if wins else 0.0
            strategy.avg_loss_ratio = round(
                sum(t.pnl_ratio or 0 for t in losses) / len(losses), 4
            ) if losses else 0.0

        await db.commit()
        await db.refresh(strategy)
        logger.info(
            f"策略统计已更新: {strategy.name} "
            f"胜率={strategy.win_rate:.1%} 共{strategy.total_count}笔"
        )
        return strategy

    @staticmethod
    async def recalc_all(db: AsyncSession) -> int:
        """重新计算所有策略的统计数据"""
        result = await db.execute(select(Strategy))
        strategies = result.scalars().all()
        for s in strategies:
            await StrategyService.recalc_stats(db, s.id)
        return len(strategies)