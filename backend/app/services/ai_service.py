"""
AI服务层 - 使用 Gemini API
- search_industry_news: Gemini + Google Search 搜索今日产业动态
- generate_articles: Gemini 生成三框架公众号文章
"""
import json
import logging
import traceback
import httpx
from datetime import date
from app.core.config import settings

logger = logging.getLogger(__name__)

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
GEMINI_MODEL = "gemini-2.5-flash-lite"


def _gemini_url(endpoint: str) -> str:
    return f"{GEMINI_BASE_URL}/models/{GEMINI_MODEL}:{endpoint}?key={settings.GEMINI_API_KEY}"


def _proxy_client(timeout: int = 60) -> httpx.AsyncClient:
    """国内需要走代理访问 Gemini"""
    if settings.PROXY_URL:
        logger.debug(f"使用代理: {settings.PROXY_URL}")
        # httpx 0.28+ 用 proxy 单参数，旧版用 proxies 字典
        # 统一用 proxy 参数兼容新版
        return httpx.AsyncClient(proxy=settings.PROXY_URL, timeout=timeout)
    logger.debug("未配置代理，直连")
    return httpx.AsyncClient(timeout=timeout)


async def search_industry_news(
    sectors: list[str],
    extra_keywords: str,
    review_date: date,
) -> dict:
    """
    调用 Gemini + Google Search 搜索今日相关板块产业信息
    返回 {"news": [...], "summary": "..."}
    """
    logger.info(f"开始搜索产业信息 | 板块: {sectors} | 日期: {review_date}")

    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY 未配置，请检查 .env 文件")

    date_str = review_date.strftime("%Y年%m月%d日")
    date_en = review_date.strftime("%Y-%m-%d")
    sector_str = "、".join(sectors)
    keyword_str = f"，补充关注：{extra_keywords}" if extra_keywords else ""

    prompt = f"""你是一个专业的A股产业信息分析师。

今天是{date_str}（{date_en}）。

请使用 google_search 搜索**今日**（{date_str}）以下A股板块的重要产业动态：
{sector_str}{keyword_str}

搜索要求：
1. 搜索时间范围严格限定在今日（{date_str}）或最近24小时内
2. 优先使用以下关键词搜索："{sector_str} {date_en}"、"{sector_str} 今日"
3. 如果今日暂无相关信息，可返回最近2个交易日内的信息，但必须在 source 里注明具体日期
4. 重点关注：政策消息、销售/产量数据、产业链动态、机构研报观点、龙头公司公告
5. 不要编造信息，没有就是没有

严格按以下JSON格式返回，不要输出任何其他内容，不要加markdown代码块：
{{
  "news": [
    {{
      "sector": "板块名称",
      "title": "新闻标题（30字以内，包含具体数据或事件名称）",
      "source": "来源名称 · 具体日期",
      "sentiment": "positive或negative或neutral",
      "sentiment_label": "利好或利空或中性"
    }}
  ],
  "summary": "产业信息综合摘要100-150字，说明今日各板块核心变化及对持仓的影响判断"
}}

注意：
- 每个板块返回2-3条，按重要性排序
- 如果某个板块今日确实没有重要消息，不返回该板块条目，不要编造
- title 里尽量包含具体数字或事件名称，不要写空洞标题"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"google_search": {}}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 2000,
        },
    }

    try:
        async with _proxy_client(60) as client:
            url = _gemini_url("generateContent")
            logger.debug(f"请求 URL: {url}")
            resp = await client.post(url, json=payload)
            logger.info(f"Gemini 响应状态码: {resp.status_code}")
            logger.debug(f"Gemini 响应前500字: {resp.text[:500]}")
            resp.raise_for_status()
            data = resp.json()

    except httpx.ProxyError as e:
        logger.error(f"代理连接失败: {e} | PROXY_URL={settings.PROXY_URL}")
        raise RuntimeError(f"代理连接失败，请确认代理已启动: {e}")
    except httpx.ConnectError as e:
        logger.error(f"网络连接失败: {e}")
        raise RuntimeError(f"网络连接失败，请检查代理配置: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Gemini API 错误: {e.response.status_code}\n{e.response.text}")
        raise RuntimeError(f"Gemini API 错误 {e.response.status_code}: {e.response.text}")
    except Exception as e:
        logger.error(f"请求 Gemini 未知异常:\n{traceback.format_exc()}")
        raise

    # 解析响应结构
    try:
        raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        logger.debug(f"Gemini 返回文本前300字: {raw[:300]}")
    except (KeyError, IndexError) as e:
        logger.error(f"解析 Gemini 响应结构失败: {e}\n完整响应: {json.dumps(data, ensure_ascii=False)}")
        raise RuntimeError("Gemini 响应格式异常，无法提取文本")

    # 清理 markdown 代码块后解析 JSON
    try:
        cleaned = raw
        if "```" in cleaned:
            for part in cleaned.split("```"):
                part = part.strip()
                if part.startswith("json"):
                    part = part[4:].strip()
                if part.startswith("{"):
                    cleaned = part
                    break

        result = json.loads(cleaned)
        logger.info(f"搜索完成，共 {len(result.get('news', []))} 条新闻")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"JSON 解析失败: {e}\n原始内容: {raw}")
        raise RuntimeError(f"AI 返回内容无法解析为 JSON: {e}")


async def generate_articles(review_data: dict) -> list[dict]:
    """
    根据完整复盘数据生成三框架公众号文章
    返回 [{"framework": "...", "title": "...", "content": "..."}]
    """
    logger.info(f"开始生成文章 | 日期: {review_data.get('date')}")

    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY 未配置，请检查 .env 文件")

    context = _build_review_context(review_data)

    frameworks = [
        {
            "key": "resonance",
            "name": "散户共鸣",
            "instruction": (
                "用第一人称写作，语气诚实且略带自嘲。"
                "把今日的真实交易经历讲成一个有情感张力的故事，"
                "重点放在情绪波动和心理活动，让普通散户产生强烈共鸣。"
                "结尾用一个开放性问题邀请读者互动。"
                "避免教训说教味，保持真实感。800-1000字。"
            ),
        },
        {
            "key": "methodology",
            "name": "方法论",
            "instruction": (
                "用客观视角提炼今日交易的规律和规则。"
                "从具体错误或成功中抽象出3-5条可立刻执行的操作规则，"
                "每条规则配真实数据或具体价格行为描述。"
                "语气专业不煽情，适合进阶投资者。"
                "结尾提出一个反问引发读者思考。900-1100字。"
            ),
        },
        {
            "key": "reflection",
            "name": "认知反思",
            "instruction": (
                "从行为金融学或心理学角度深度解读今日交易决策。"
                "引用具体的认知偏差概念（如后见之偏、锚定效应、处置效应等），"
                "分析交易背后的心理机制。"
                "语言有哲学感，适合高知读者。"
                "结尾提出一个开放性哲学问题。1000-1200字。"
            ),
        },
    ]

    results = []
    for fw in frameworks:
        logger.info(f"生成框架: {fw['name']}")
        try:
            article = await _generate_single_article(context, fw)
            results.append(article)
        except Exception as e:
            logger.error(f"生成 {fw['name']} 失败:\n{traceback.format_exc()}")
            raise

    logger.info("三框架文章全部生成完成")
    return results


def _build_review_context(d: dict) -> str:
    lines = [
        f"【复盘日期】{d.get('date', '')}",
        f"【今日盈亏】{d.get('pnl_amount', 0):+.0f}元  操作{d.get('trade_count', 0)}笔  {d.get('win_count', 0)}胜{d.get('loss_count', 0)}负",
        "",
        "=== 盘面梳理 ===",
        f"大盘研判：{d.get('market_overview', '')}",
        f"研判准确度：{d.get('plan_accuracy', '')}",
        f"主导风格：{d.get('market_style', '')}  大小盘分化：{d.get('market_split', '')}",
        f"风格描述：{d.get('style_desc', '')}",
        f"领涨板块：{d.get('leading_sectors', '')}",
        f"领跌板块：{d.get('lagging_sectors', '')}",
        f"板块主线：{d.get('sector_summary', '')}",
        "",
        "=== 产业信息 ===",
        d.get('industry_summary', ''),
        "",
        "=== 操作复盘 ===",
        f"最符合计划：{d.get('best_trade', '')}",
        f"最偏离计划：{d.get('worst_trade', '')}",
        f"情绪状态：{d.get('emotion_state', '')}",
        f"今日教训：{d.get('key_lesson', '')}",
        f"反事实思考：{d.get('counterfactual', '')}",
        f"明日假设：{d.get('next_hypothesis', '')}",
        f"运气占比：{d.get('luck_ratio', '')}",
    ]
    return "\n".join(lines)


async def _generate_single_article(context: str, framework: dict) -> dict:
    prompt = f"""你是一个专业的A股投资类公众号作者，擅长写{framework['name']}风格的文章。

写作要求：{framework['instruction']}

格式要求：
- 第一行是文章标题，之后空一行是正文
- 正文用自然段落，不用markdown标题符号
- 文章末尾加一行：非投资建议，仅记录个人复盘

请根据以下今日复盘内容写文章：

{context}"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 3000,
        },
    }

    try:
        async with _proxy_client(90) as client:
            resp = await client.post(_gemini_url("generateContent"), json=payload)
            logger.info(f"文章生成响应状态码: {resp.status_code}")
            logger.debug(f"文章生成响应前300字: {resp.text[:300]}")
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"文章生成 API 错误: {e.response.status_code}\n{e.response.text}")
        raise RuntimeError(f"Gemini API 错误 {e.response.status_code}")
    except Exception as e:
        logger.error(f"文章生成请求异常:\n{traceback.format_exc()}")
        raise

    try:
        raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError) as e:
        logger.error(f"解析文章响应失败: {e}\n完整响应: {json.dumps(data, ensure_ascii=False)}")
        raise RuntimeError("Gemini 文章响应格式异常")

    lines = raw.split("\n")
    title = lines[0].strip().lstrip("#").strip()
    content = "\n".join(lines[1:]).strip()

    return {
        "framework": framework["key"],
        "title": title,
        "content": content,
    }
