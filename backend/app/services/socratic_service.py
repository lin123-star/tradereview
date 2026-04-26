import json
import logging
import traceback
import httpx
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.socratic import SocraticSession
from app.models.trade import Trade
from app.core.config import settings

logger = logging.getLogger(__name__)

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
GEMINI_MODEL = "gemini-2.5-flash-lite"
MAX_ROUNDS = 4


def _gemini_url(endpoint: str) -> str:
    return f"{GEMINI_BASE_URL}/models/{GEMINI_MODEL}:{endpoint}?key={settings.GEMINI_API_KEY}"


def _proxy_client(timeout: int = 60) -> httpx.AsyncClient:
    if settings.PROXY_URL:
        return httpx.AsyncClient(proxy=settings.PROXY_URL, timeout=timeout)
    return httpx.AsyncClient(timeout=timeout)


# 每次都附在消息末尾，强制 JSON 输出
JSON_FORMAT_REMINDER = """

【强制格式要求】只能输出以下JSON，不允许有任何其他文字：
{
  "question": "你的质疑性问题或总结（100字以内）",
  "blind_spots": ["已识别的盲区1", "已识别的盲区2"],
  "is_complete": false
}"""

SYSTEM_PROMPT = """你是一个专业的交易心理教练，采用苏格拉底式对话审讯交易者的决策。

规则：
1. 每次只问一个问题，针对具体细节
2. 绝对不给正面评价
3. 对盈利和亏损交易同等力度质疑
4. 重点质疑：止损是否提前设定、是否三层验证、情绪影响、运气成分

常见盲区：事后止损、忽略大盘、逻辑矛盾、幸存偏差、计划外操作"""


def _build_trade_context(trade: Trade) -> str:
    direction_map = {"buy": "买入", "sell": "卖出", "add": "加仓", "reduce": "减仓"}
    emotion_map = {"calm": "冷静", "greedy": "贪婪", "panic": "恐慌",
                   "hesitant": "犹豫", "impulsive": "冲动"}
    strategy_map = {"trend": "趋势跟踪", "reversal": "反转",
                    "news": "消息面", "quant": "量化信号", "other": "其他"}

    pnl_str = ""
    if trade.pnl_amount is not None:
        sign = "+" if trade.pnl_amount >= 0 else ""
        pnl_str = f"{sign}{trade.pnl_amount:.0f}元（{sign}{trade.pnl_ratio * 100:.2f}%）"
    else:
        pnl_str = "持仓中，未出场"

    lines = [
        f"【标的】{trade.symbol} {trade.name}",
        f"【方向】{direction_map.get(trade.direction, trade.direction)}",
        f"【入场价】{trade.entry_price}  【出场价】{trade.exit_price or '未出场'}",
        f"【盈亏】{pnl_str}",
        f"【仓位】{trade.position_ratio * 100:.0f}%",
        f"【入场情绪】{emotion_map.get(trade.emotion, trade.emotion)}",
        f"【出场情绪】{emotion_map.get(trade.exit_emotion, trade.exit_emotion)}",
        f"【策略类型】{strategy_map.get(trade.strategy, trade.strategy)}",
        f"【是否符合计划】{trade.plan_followed}",
        "",
        "【入场逻辑（锁定）】",
        trade.entry_logic or "（未填写）",
        "",
        "【出场逻辑】",
        trade.exit_logic or "（未填写）",
        "",
        f"【自述教训】{trade.lesson or '（未填写）'}",
    ]
    return "\n".join(lines)


def _parse_response(raw: str) -> dict:
    """
    解析 Gemini 返回内容。
    Gemini 有时不遵守 JSON 格式要求，这里做兜底处理。
    """
    if not raw:
        raise ValueError("Gemini 返回内容为空")

    cleaned = raw.strip()

    # 清理 markdown 代码块
    if "```" in cleaned:
        for part in cleaned.split("```"):
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{"):
                cleaned = part
                break

    # 尝试直接解析 JSON
    if cleaned.startswith("{"):
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON解析失败: {e}，尝试兜底处理")

    # 兜底：Gemini 返回了纯文本，把它包装成标准格式
    logger.warning(f"Gemini 未返回JSON，兜底包装。原始: {raw[:200]}")
    return {
        "question": raw.strip(),
        "blind_spots": [],
        "is_complete": False,
    }


async def _call_gemini(messages_for_api: list) -> dict:
    """调用 Gemini API，使用 JSON 模式强制输出结构化内容"""
    payload = {
        "contents": messages_for_api,
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 800,
            "responseMimeType": "application/json",  # 强制JSON输出
        },
    }

    async with _proxy_client(60) as client:
        resp = await client.post(_gemini_url("generateContent"), json=payload)
        logger.info(f"Gemini 审讯响应状态码: {resp.status_code}")
        logger.debug(f"Gemini 审讯返回前500字: {resp.text[:500]}")
        resp.raise_for_status()
        data = resp.json()

    raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    return _parse_response(raw)


class SocraticService:

    @staticmethod
    async def get_or_create_session(
        db: AsyncSession, trade_id: int
    ) -> SocraticSession:
        result = await db.execute(
            select(SocraticSession)
            .where(SocraticSession.trade_id == trade_id)
            .order_by(SocraticSession.created_at.desc())
        )
        session = result.scalar_one_or_none()

        if session is None or session.status == "completed":
            session = SocraticSession(
                trade_id=trade_id,
                messages=[],
                blind_spots=[],
                summary="",
                status="active",
            )
            db.add(session)
            await db.commit()
            await db.refresh(session)
            logger.info(f"创建新审讯会话: trade_id={trade_id} session_id={session.id}")

        return session

    @staticmethod
    async def get_session(
        db: AsyncSession, session_id: int
    ) -> Optional[SocraticSession]:
        result = await db.execute(
            select(SocraticSession).where(SocraticSession.id == session_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def start(db: AsyncSession, trade_id: int) -> tuple[SocraticSession, str]:
        """开始或继续审讯"""
        trade_result = await db.execute(select(Trade).where(Trade.id == trade_id))
        trade = trade_result.scalar_one_or_none()
        if not trade:
            raise ValueError(f"交易记录 {trade_id} 不存在")

        session = await SocraticService.get_or_create_session(db, trade_id)

        # 已有对话历史，返回最后一条 AI 消息
        if session.messages:
            last_ai = next(
                (m for m in reversed(session.messages) if m["role"] == "ai"),
                None
            )
            if last_ai:
                return session, last_ai["content"]

        trade_context = _build_trade_context(trade)

        first_prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"以下是需要审讯的交易记录：\n\n{trade_context}\n\n"
            f"请提出第一个质疑性问题。"
            f"{JSON_FORMAT_REMINDER}"
        )

        messages_for_api = [
            {"role": "user", "parts": [{"text": first_prompt}]}
        ]

        try:
            result = await _call_gemini(messages_for_api)
            ai_question = result.get("question", "")
            blind_spots = result.get("blind_spots", [])

            session.messages = [{"role": "ai", "content": ai_question}]
            session.blind_spots = blind_spots

            trade.review_status = "reviewing"
            await db.commit()
            await db.refresh(session)

            logger.info(f"审讯开始 session_id={session.id}")
            return session, ai_question

        except Exception as e:
            logger.error(f"审讯首问失败:\n{traceback.format_exc()}")
            raise RuntimeError(f"AI审讯启动失败: {e}")

    @staticmethod
    async def reply(
        db: AsyncSession,
        session_id: int,
        user_message: str,
    ) -> dict:
        """用户回答后，AI继续追问"""
        session = await SocraticService.get_session(db, session_id)
        if not session:
            raise ValueError(f"审讯会话 {session_id} 不存在")
        if session.status == "completed":
            raise ValueError("该审讯已结束")

        trade_result = await db.execute(
            select(Trade).where(Trade.id == session.trade_id)
        )
        trade = trade_result.scalar_one_or_none()
        trade_context = _build_trade_context(trade)

        messages = list(session.messages)
        messages.append({"role": "user", "content": user_message})

        user_count = sum(1 for m in messages if m["role"] == "user")
        is_last_round = user_count >= MAX_ROUNDS

        # ── 构建 Gemini 多轮对话 ──────────────────────
        # Gemini 要求严格交替的 user/model 角色
        # 把背景信息放在第一个 user turn，第一条AI消息作为第一个 model turn
        background = (
            f"{SYSTEM_PROMPT}\n\n"
            f"交易记录：\n{trade_context}\n\n"
            f"已识别盲区：{session.blind_spots}"
        )

        first_ai = messages[0]["content"] if messages and messages[0]["role"] == "ai" else ""

        api_messages = [
            {"role": "user", "parts": [{"text": background}]}
        ]
        if first_ai:
            api_messages.append({
                "role": "model",
                "parts": [{"text": first_ai}]
            })

        # 后续对话轮次（从第一条user消息开始）
        for msg in messages[1:]:
            role = "model" if msg["role"] == "ai" else "user"
            api_messages.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })

        # 在最后一条 user 消息追加 JSON 格式要求
        suffix = JSON_FORMAT_REMINDER
        if is_last_round:
            suffix = (
                "\n\n（最后一轮：请将 is_complete 设为 true，"
                "在 question 字段写审讯总结，列出所有认知盲区和未厘清的问题。）"
                + JSON_FORMAT_REMINDER
            )

        api_messages[-1]["parts"][0]["text"] += suffix

        try:
            result = await _call_gemini(api_messages)
            ai_response = result.get("question", "")
            new_blind_spots = result.get("blind_spots", [])
            is_complete = result.get("is_complete", False) or is_last_round

            all_blind_spots = list(dict.fromkeys(
                session.blind_spots + new_blind_spots
            ))

            messages.append({"role": "ai", "content": ai_response})
            session.messages = messages
            session.blind_spots = all_blind_spots

            summary = ""
            if is_complete:
                session.status = "completed"
                session.summary = ai_response
                summary = ai_response
                if trade:
                    trade.review_status = "done"
                logger.info(f"审讯完成 session_id={session_id} 盲区: {all_blind_spots}")

            await db.commit()
            await db.refresh(session)

            return {
                "session_id": session_id,
                "ai_message": ai_response,
                "blind_spots": all_blind_spots,
                "status": session.status,
                "summary": summary,
            }

        except Exception as e:
            logger.error(f"审讯追问失败:\n{traceback.format_exc()}")
            raise RuntimeError(f"AI追问失败: {e}")

    @staticmethod
    async def get_sessions_by_trade(
        db: AsyncSession, trade_id: int
    ) -> list[SocraticSession]:
        result = await db.execute(
            select(SocraticSession)
            .where(SocraticSession.trade_id == trade_id)
            .order_by(SocraticSession.created_at.desc())
        )
        return result.scalars().all()