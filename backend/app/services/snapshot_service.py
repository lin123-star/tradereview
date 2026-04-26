"""
快照服务：在交易入场/出场时触发行情抓取，存入数据库
"""
import logging
import traceback
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.market_snapshot import MarketSnapshot
from app.models.trade import Trade
from app.services.market_data_service import fetch_market_snapshot

logger = logging.getLogger(__name__)


class SnapshotService:

    @staticmethod
    async def create_entry_snapshot(
        db: AsyncSession, trade: Trade
    ) -> MarketSnapshot | None:
        """入场时创建行情快照（异步后台执行）"""
        if not trade.entry_time:
            return None
        snapshot_date = trade.entry_time.date()
        return await SnapshotService._fetch_and_save(
            db, trade, snapshot_date, "entry"
        )

    @staticmethod
    async def create_exit_snapshot(
        db: AsyncSession, trade: Trade
    ) -> MarketSnapshot | None:
        """出场时创建行情快照"""
        if not trade.exit_time:
            return None
        snapshot_date = trade.exit_time.date()
        return await SnapshotService._fetch_and_save(
            db, trade, snapshot_date, "exit"
        )

    @staticmethod
    async def _fetch_and_save(
        db: AsyncSession,
        trade: Trade,
        snapshot_date: date,
        snapshot_type: str,
    ) -> MarketSnapshot | None:
        """抓取行情并保存"""
        # 检查是否已有快照
        existing = await db.execute(
            select(MarketSnapshot).where(
                MarketSnapshot.trade_id == trade.id,
                MarketSnapshot.snapshot_type == snapshot_type,
            )
        )
        if existing.scalar_one_or_none():
            logger.info(f"快照已存在: trade_id={trade.id} type={snapshot_type}")
            return None

        # 创建占位记录
        snapshot = MarketSnapshot(
            trade_id=trade.id,
            snapshot_date=snapshot_date,
            snapshot_type=snapshot_type,
            symbol=trade.symbol,
            fetch_status="pending",
        )
        db.add(snapshot)
        await db.commit()
        await db.refresh(snapshot)

        # 异步抓取行情数据
        try:
            logger.info(f"开始抓取行情快照: {trade.symbol} {snapshot_date} {snapshot_type}")
            data = await fetch_market_snapshot(trade.symbol, snapshot_date)

            # 更新快照记录
            for key, val in data.items():
                if hasattr(snapshot, key):
                    setattr(snapshot, key, val)

            await db.commit()
            await db.refresh(snapshot)
            logger.info(f"行情快照保存成功: trade_id={trade.id} {snapshot_type}")
            return snapshot

        except Exception as e:
            logger.error(f"行情快照抓取失败: trade_id={trade.id}\n{traceback.format_exc()}")
            snapshot.fetch_status = "failed"
            snapshot.fetch_error = str(e)[:200]
            await db.commit()
            return snapshot

    @staticmethod
    async def get_by_trade(
        db: AsyncSession, trade_id: int
    ) -> list[MarketSnapshot]:
        result = await db.execute(
            select(MarketSnapshot)
            .where(MarketSnapshot.trade_id == trade_id)
            .order_by(MarketSnapshot.snapshot_type)
        )
        return result.scalars().all()

    @staticmethod
    async def retry_failed(db: AsyncSession) -> int:
        """重试所有失败的快照抓取"""
        result = await db.execute(
            select(MarketSnapshot).where(
                MarketSnapshot.fetch_status.in_(["failed", "pending"])
            )
        )
        snapshots = result.scalars().all()
        retried = 0

        for snap in snapshots:
            # 获取对应的交易记录
            trade_result = await db.execute(
                select(Trade).where(Trade.id == snap.trade_id)
            )
            trade = trade_result.scalar_one_or_none()
            if not trade:
                continue

            try:
                data = await fetch_market_snapshot(snap.symbol, snap.snapshot_date)
                for key, val in data.items():
                    if hasattr(snap, key):
                        setattr(snap, key, val)
                await db.commit()
                retried += 1
                logger.info(f"重试成功: snapshot_id={snap.id}")
            except Exception as e:
                logger.warning(f"重试失败: snapshot_id={snap.id} {e}")

        return retried