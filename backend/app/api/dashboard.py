import logging
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.core.database import get_db
from app.models.trade import Trade
from app.models.daily_review import DailyReview
from app.models.daily_plan import DailyPlan
from app.models.socratic import SocraticSession
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dashboard", tags=["仪表台"])


class DashboardData(BaseModel):
    # 今日
    today: str
    today_pnl: float
    today_trade_count: int
    today_plan_locked: bool
    today_review_done: bool

    # 本月统计
    month_pnl: float
    month_trade_count: int
    month_win_count: int
    month_loss_count: int
    month_win_rate: float
    month_avg_pnl_ratio: float

    # 待办
    pending_review_count: int    # 待复盘交易数
    pending_audit_count: int     # 待审讯交易数

    # 认知盲区 Top3
    top_blind_spots: list[str]

    # 近30日盈亏曲线 [{"date": "2026-04-01", "pnl": 1200.0}]
    pnl_curve: list[dict]

    # 情绪胜率统计 [{"emotion": "calm", "win_rate": 0.78, "count": 12}]
    emotion_stats: list[dict]

    # 近期交易（最新5笔）
    recent_trades: list[dict]


@router.get("", response_model=DashboardData)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    today = date.today()
    today_str = today.isoformat()
    month_start = today.replace(day=1)
    thirty_days_ago = today - timedelta(days=30)

    # ── 今日计划状态 ──────────────────────────────────
    plan_result = await db.execute(
        select(DailyPlan).where(DailyPlan.date == today)
    )
    today_plan = plan_result.scalar_one_or_none()
    today_plan_locked = today_plan.locked if today_plan else False

    # ── 今日复盘状态 ──────────────────────────────────
    review_result = await db.execute(
        select(DailyReview).where(DailyReview.date == today)
    )
    today_review = review_result.scalar_one_or_none()
    today_review_done = today_review is not None

    # ── 今日盈亏（今日出场的交易） ────────────────────
    today_trades_result = await db.execute(
        select(Trade).where(
            and_(
                Trade.status == "closed",
                func.date(Trade.exit_time) == today_str,
            )
        )
    )
    today_trades = today_trades_result.scalars().all()
    today_pnl = sum(t.pnl_amount or 0 for t in today_trades)
    today_trade_count = len(today_trades)

    # ── 本月统计 ──────────────────────────────────────
    month_trades_result = await db.execute(
        select(Trade).where(
            and_(
                Trade.status == "closed",
                Trade.exit_time >= datetime.combine(month_start, datetime.min.time()),
            )
        )
    )
    month_trades = month_trades_result.scalars().all()
    month_trade_count = len(month_trades)
    month_win = [t for t in month_trades if (t.pnl_amount or 0) > 0]
    month_loss = [t for t in month_trades if (t.pnl_amount or 0) <= 0]
    month_win_count = len(month_win)
    month_loss_count = len(month_loss)
    month_win_rate = month_win_count / month_trade_count if month_trade_count else 0
    month_pnl = sum(t.pnl_amount or 0 for t in month_trades)
    month_avg_pnl_ratio = (
        sum(t.pnl_ratio or 0 for t in month_trades) / month_trade_count
        if month_trade_count else 0
    )

    # ── 待办统计 ──────────────────────────────────────
    pending_review_result = await db.execute(
        select(func.count()).select_from(Trade).where(
            and_(Trade.status == "closed", Trade.review_status == "pending")
        )
    )
    pending_review_count = pending_review_result.scalar() or 0

    pending_audit_result = await db.execute(
        select(func.count()).select_from(Trade).where(
            and_(Trade.status == "closed", Trade.review_status == "reviewing")
        )
    )
    pending_audit_count = pending_audit_result.scalar() or 0

    # ── 认知盲区 Top3 ─────────────────────────────────
    sessions_result = await db.execute(
        select(SocraticSession).where(SocraticSession.status == "completed")
    )
    sessions = sessions_result.scalars().all()
    blind_spot_counter: dict[str, int] = {}
    for s in sessions:
        for bs in (s.blind_spots or []):
            blind_spot_counter[bs] = blind_spot_counter.get(bs, 0) + 1
    top_blind_spots = sorted(
        blind_spot_counter, key=blind_spot_counter.get, reverse=True
    )[:3]

    # ── 近30日盈亏曲线 ────────────────────────────────
    curve_result = await db.execute(
        select(Trade).where(
            and_(
                Trade.status == "closed",
                Trade.exit_time >= datetime.combine(thirty_days_ago, datetime.min.time()),
            )
        ).order_by(Trade.exit_time)
    )
    curve_trades = curve_result.scalars().all()

    # 按日期聚合
    daily_pnl: dict[str, float] = {}
    for t in curve_trades:
        if t.exit_time:
            d = t.exit_time.strftime("%Y-%m-%d")
            daily_pnl[d] = daily_pnl.get(d, 0) + (t.pnl_amount or 0)

    pnl_curve = [{"date": d, "pnl": round(v, 2)} for d, v in sorted(daily_pnl.items())]

    # ── 情绪胜率统计 ──────────────────────────────────
    emotion_map: dict[str, dict] = {}
    for t in month_trades:
        e = t.emotion or "unknown"
        if e not in emotion_map:
            emotion_map[e] = {"win": 0, "total": 0}
        emotion_map[e]["total"] += 1
        if (t.pnl_amount or 0) > 0:
            emotion_map[e]["win"] += 1

    emotion_label = {
        "calm": "冷静", "greedy": "贪婪", "panic": "恐慌",
        "hesitant": "犹豫", "impulsive": "冲动", "unknown": "未标记"
    }
    emotion_stats = [
        {
            "emotion": emotion_label.get(e, e),
            "win_rate": round(v["win"] / v["total"], 4) if v["total"] else 0,
            "count": v["total"],
        }
        for e, v in emotion_map.items()
    ]
    emotion_stats.sort(key=lambda x: x["win_rate"], reverse=True)

    # ── 近期交易（最新5笔） ────────────────────────────
    recent_result = await db.execute(
        select(Trade).order_by(Trade.created_at.desc()).limit(5)
    )
    recent_trades_raw = recent_result.scalars().all()
    direction_label = {"buy": "买入", "sell": "卖出", "add": "加仓", "reduce": "减仓"}
    recent_trades = [
        {
            "id": t.id,
            "symbol": t.symbol,
            "name": t.name,
            "direction": direction_label.get(t.direction, t.direction),
            "entry_price": t.entry_price,
            "exit_price": t.exit_price,
            "pnl_amount": t.pnl_amount,
            "pnl_ratio": t.pnl_ratio,
            "status": t.status,
            "review_status": t.review_status,
            "emotion": emotion_label.get(t.emotion, t.emotion),
            "entry_time": t.entry_time.isoformat() if t.entry_time else None,
        }
        for t in recent_trades_raw
    ]

    return DashboardData(
        today=today_str,
        today_pnl=round(today_pnl, 2),
        today_trade_count=today_trade_count,
        today_plan_locked=today_plan_locked,
        today_review_done=today_review_done,
        month_pnl=round(month_pnl, 2),
        month_trade_count=month_trade_count,
        month_win_count=month_win_count,
        month_loss_count=month_loss_count,
        month_win_rate=round(month_win_rate, 4),
        month_avg_pnl_ratio=round(month_avg_pnl_ratio, 4),
        pending_review_count=pending_review_count,
        pending_audit_count=pending_audit_count,
        top_blind_spots=top_blind_spots,
        pnl_curve=pnl_curve,
        emotion_stats=emotion_stats,
        recent_trades=recent_trades,
    )