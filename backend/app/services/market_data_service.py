"""
行情数据抓取服务
使用 AKShare 抓取个股和大盘数据，存入 market_snapshots 表
"""
import logging
import traceback
from datetime import date, timedelta
from typing import Optional
import asyncio

logger = logging.getLogger(__name__)


def _to_trade_date(d: date) -> str:
    """转换为 AKShare 需要的日期格式 YYYYMMDD"""
    return d.strftime("%Y%m%d")


def _safe_float(val) -> Optional[float]:
    """安全转换为 float，失败返回 None"""
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


async def fetch_market_snapshot(
    symbol: str,
    snapshot_date: date,
) -> dict:
    """
    抓取指定日期的行情快照
    symbol: 如 "600519"（不带市场前缀）
    snapshot_date: 抓取日期
    返回 dict，字段对应 MarketSnapshot 模型
    """
    # AKShare 是同步库，放到线程池执行避免阻塞
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None, _fetch_sync, symbol, snapshot_date
    )
    return result


def _fetch_sync(symbol: str, snapshot_date: date) -> dict:
    """同步抓取，在线程池中执行"""
    try:
        import akshare as ak
    except ImportError:
        raise RuntimeError("请先安装 akshare: pip install akshare")

    date_str = _to_trade_date(snapshot_date)
    # 往前多取20个交易日，用于计算均线
    start_date = _to_trade_date(snapshot_date - timedelta(days=40))

    result = {
        "fetch_status": "done",
        "fetch_error": "",
        # 大盘
        "sh_pct": None, "sz_pct": None, "cy_pct": None,
        "sh_volume_ratio": None, "market_trend": "",
        # 个股
        "stock_pct": None, "stock_volume": None,
        "stock_volume_ratio": None, "stock_turnover": None,
        "stock_close": None,
        # 均线
        "ma5": None, "ma10": None, "ma20": None,
        "above_ma5": None, "above_ma10": None, "above_ma20": None,
        "ma_bullish": None,
        # MACD
        "macd_diff": None, "macd_dea": None,
        "macd_bar": None, "macd_golden_cross": None,
        # 板块
        "sector_name": "", "sector_pct": None, "sector_rank": None,
    }

    # ── 1. 大盘数据 ──────────────────────────────────
    try:
        result.update(_fetch_index_data(ak, date_str))
    except Exception as e:
        logger.warning(f"大盘数据抓取失败: {e}")

    # ── 2. 个股日线数据（含均线MACD） ────────────────
    try:
        result.update(_fetch_stock_data(ak, symbol, start_date, date_str))
    except Exception as e:
        logger.warning(f"个股数据抓取失败 {symbol}: {e}")
        result["fetch_status"] = "partial"
        result["fetch_error"] = str(e)[:200]

    # ── 3. 板块数据 ──────────────────────────────────
    try:
        result.update(_fetch_sector_data(ak, symbol, date_str))
    except Exception as e:
        logger.warning(f"板块数据抓取失败: {e}")

    logger.info(
        f"行情快照抓取完成 | {symbol} {snapshot_date} "
        f"| 个股涨跌: {result.get('stock_pct')}% "
        f"| 上证: {result.get('sh_pct')}%"
    )
    return result


def _fetch_index_data(ak, date_str: str) -> dict:
    """抓取大盘指数数据"""
    result = {}

    index_map = {
        "000001": ("sh_pct", "sh_volume_ratio"),   # 上证
        "399001": ("sz_pct", None),                 # 深证
        "399006": ("cy_pct", None),                 # 创业板
    }

    for code, (pct_key, vol_key) in index_map.items():
        try:
            df = ak.stock_zh_index_daily(symbol=f"sh{code}" if code.startswith("0") else f"sz{code}")
            if df is None or df.empty:
                continue
            df["date"] = df["date"].astype(str).str.replace("-", "")
            row = df[df["date"] == date_str]
            if row.empty:
                # 尝试取最近一个交易日
                row = df[df["date"] <= date_str].tail(1)
            if not row.empty:
                close = _safe_float(row.iloc[-1]["close"])
                prev_close = None
                idx = df.index.get_loc(row.index[-1])
                if idx > 0:
                    prev_close = _safe_float(df.iloc[idx - 1]["close"])
                if close and prev_close and prev_close > 0:
                    pct = round((close - prev_close) / prev_close * 100, 2)
                    result[pct_key] = pct

                if vol_key:
                    # 量能比：今日量/5日均量
                    vol = _safe_float(row.iloc[-1].get("volume"))
                    recent = df.tail(6)
                    if len(recent) >= 6 and vol:
                        avg_vol = recent.iloc[:-1]["volume"].astype(float).mean()
                        if avg_vol > 0:
                            result[vol_key] = round(vol / avg_vol, 2)
        except Exception as e:
            logger.debug(f"指数 {code} 抓取失败: {e}")

    # 判断大盘趋势
    sh_pct = result.get("sh_pct")
    if sh_pct is not None:
        if sh_pct > 0.5:
            result["market_trend"] = "up"
        elif sh_pct < -0.5:
            result["market_trend"] = "down"
        else:
            result["market_trend"] = "sideways"

    return result


def _fetch_stock_data(ak, symbol: str, start_date: str, end_date: str) -> dict:
    """抓取个股日线数据，计算均线和MACD"""
    result = {}

    # 判断市场前缀
    prefix = "sh" if symbol.startswith("6") else "sz"
    full_symbol = f"{prefix}{symbol}"

    # 获取日线数据
    df = ak.stock_zh_a_hist(
        symbol=symbol,
        period="daily",
        start_date=start_date,
        end_date=end_date,
        adjust="qfq",  # 前复权
    )

    if df is None or df.empty:
        raise ValueError(f"未获取到 {symbol} 的行情数据")

    # 统一列名（AKShare不同版本列名可能不同）
    col_map = {
        "日期": "date", "开盘": "open", "收盘": "close",
        "最高": "high", "最低": "low", "成交量": "volume",
        "成交额": "amount", "换手率": "turnover",
        "涨跌幅": "pct_chg",
    }
    df = df.rename(columns=col_map)
    df["date"] = df["date"].astype(str).str.replace("-", "")
    df = df.sort_values("date").reset_index(drop=True)

    # 取目标日期的数据
    target = df[df["date"] <= end_date].tail(1)
    if target.empty:
        raise ValueError(f"{symbol} 在 {end_date} 无数据")

    row = target.iloc[-1]
    idx = target.index[-1]

    result["stock_close"] = _safe_float(row.get("close"))
    result["stock_pct"] = _safe_float(row.get("pct_chg"))
    result["stock_turnover"] = _safe_float(row.get("turnover"))

    # 成交量（万手）
    vol = _safe_float(row.get("volume"))
    if vol:
        result["stock_volume"] = round(vol / 10000, 2)
        # 量能比
        if idx >= 5:
            avg_vol = df.iloc[max(0, idx-5):idx]["volume"].astype(float).mean()
            if avg_vol > 0:
                result["stock_volume_ratio"] = round(vol / avg_vol, 2)

    # ── 计算均线 ──────────────────────────────────────
    closes = df["close"].astype(float)
    close_now = result["stock_close"]

    if idx >= 4:
        ma5 = closes.iloc[idx-4:idx+1].mean()
        result["ma5"] = round(ma5, 3)
        if close_now:
            result["above_ma5"] = 1 if close_now > ma5 else 0

    if idx >= 9:
        ma10 = closes.iloc[idx-9:idx+1].mean()
        result["ma10"] = round(ma10, 3)
        if close_now:
            result["above_ma10"] = 1 if close_now > ma10 else 0

    if idx >= 19:
        ma20 = closes.iloc[idx-19:idx+1].mean()
        result["ma20"] = round(ma20, 3)
        if close_now:
            result["above_ma20"] = 1 if close_now > ma20 else 0

    # 均线多头排列
    ma5 = result.get("ma5")
    ma10 = result.get("ma10")
    ma20 = result.get("ma20")
    if ma5 and ma10 and ma20:
        result["ma_bullish"] = 1 if ma5 > ma10 > ma20 else 0

    # ── 计算 MACD ─────────────────────────────────────
    if len(df) >= 26:
        macd_result = _calc_macd(closes.tolist(), idx)
        result.update(macd_result)

    return result


def _calc_macd(closes: list, idx: int) -> dict:
    """手动计算 MACD（不依赖额外库）"""
    result = {}
    try:
        # EMA12 EMA26
        def ema(data, period):
            k = 2 / (period + 1)
            ema_val = data[0]
            for v in data[1:]:
                ema_val = v * k + ema_val * (1 - k)
            return ema_val

        window = closes[:idx+1]
        if len(window) < 26:
            return result

        ema12 = ema(window, 12)
        ema26 = ema(window, 26)
        diff = ema12 - ema26

        # DEA (9日EMA of DIFF)
        diffs = []
        for i in range(max(0, idx-34), idx+1):
            w = closes[:i+1]
            if len(w) >= 26:
                e12 = ema(w, 12)
                e26 = ema(w, 26)
                diffs.append(e12 - e26)

        if len(diffs) >= 9:
            dea = ema(diffs, 9)
            bar = (diff - dea) * 2

            result["macd_diff"] = round(diff, 4)
            result["macd_dea"] = round(dea, 4)
            result["macd_bar"] = round(bar, 4)

            # 判断金叉死叉（与前一日对比）
            if len(diffs) >= 2:
                prev_diff = diffs[-2]
                prev_dea = ema(diffs[:-1], 9) if len(diffs) > 9 else dea
                if prev_diff < prev_dea and diff > dea:
                    result["macd_golden_cross"] = 1  # 金叉
                elif prev_diff > prev_dea and diff < dea:
                    result["macd_golden_cross"] = -1  # 死叉
                else:
                    result["macd_golden_cross"] = 0
    except Exception as e:
        logger.debug(f"MACD计算失败: {e}")

    return result


def _fetch_sector_data(ak, symbol: str, date_str: str) -> dict:
    """抓取个股所属板块数据"""
    result = {}
    try:
        # 获取个股所属行业板块
        df = ak.stock_board_industry_cons_em(symbol=symbol)
        if df is not None and not df.empty:
            # 取第一个行业板块
            sector = df.iloc[0].get("板块名称", "") or df.iloc[0].get("名称", "")
            result["sector_name"] = str(sector)

            # 获取该板块当日涨跌幅
            if sector:
                try:
                    board_df = ak.stock_board_industry_hist_em(
                        symbol=sector,
                        start_date=date_str,
                        end_date=date_str,
                        period="日k",
                        adjust="",
                    )
                    if board_df is not None and not board_df.empty:
                        pct = _safe_float(board_df.iloc[-1].get("涨跌幅"))
                        result["sector_pct"] = pct
                except Exception as e:
                    logger.debug(f"板块涨跌幅抓取失败: {e}")
    except Exception as e:
        logger.debug(f"板块信息抓取失败: {e}")

    return result