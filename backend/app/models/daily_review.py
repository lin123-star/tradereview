from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Float, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class DailyReview(Base):
    """每日复盘主表"""
    __tablename__ = "daily_reviews"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, nullable=False, index=True, comment="复盘日期")

    # ── 当日盈亏摘要 ──────────────────────────────
    pnl_amount = Column(Float, default=0.0, comment="今日盈亏金额（元）")
    trade_count = Column(Integer, default=0, comment="操作笔数")
    win_count = Column(Integer, default=0, comment="盈利笔数")
    loss_count = Column(Integer, default=0, comment="亏损笔数")

    # ── 一、盘面梳理 ──────────────────────────────
    market_overview = Column(Text, default="", comment="大盘整体研判描述")
    plan_accuracy = Column(String(20), default="", comment="与早盘研判对比")
    market_style = Column(String(50), default="", comment="今日主导风格")
    market_split = Column(String(50), default="", comment="大小盘分化方向")
    style_desc = Column(Text, default="", comment="风格描述")
    leading_sectors = Column(Text, default="", comment="领涨板块")
    lagging_sectors = Column(Text, default="", comment="领跌板块")
    sector_summary = Column(Text, default="", comment="板块主线总结")

    # ── 二、产业信息 ──────────────────────────────
    selected_sectors = Column(JSON, default=list, comment="选择的搜索板块")
    extra_keywords = Column(String(200), default="", comment="补充搜索关键词")
    ai_news_result = Column(JSON, default=list, comment="AI搜索新闻列表")
    industry_summary = Column(Text, default="", comment="产业信息摘要")

    # ── 三、操作复盘 ──────────────────────────────
    vs_rows = Column(JSON, default=list, comment="计划vs实际对比行列表")
    best_trade = Column(Text, default="", comment="最符合计划的操作")
    worst_trade = Column(Text, default="", comment="最偏离计划/执行纪律备注")
    emotion_state = Column(String(30), default="", comment="今日情绪状态")
    key_lesson = Column(Text, default="", comment="今日最重要的教训")
    counterfactual = Column(Text, default="", comment="反事实思考")
    next_hypothesis = Column(Text, default="", comment="明日可验证假设")
    luck_ratio = Column(String(30), default="", comment="运气占比判断")

    # ── 元数据 ────────────────────────────────────
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<DailyReview date={self.date} pnl={self.pnl_amount}>"


class GeneratedArticle(Base):
    """文章工坊生成的文章"""
    __tablename__ = "generated_articles"

    id = Column(Integer, primary_key=True, index=True)
    review_date = Column(Date, nullable=False, index=True, comment="来源复盘日期")
    framework = Column(String(20), nullable=False, comment="resonance/methodology/reflection")
    title = Column(Text, default="", comment="文章标题")
    content = Column(Text, default="", comment="文章正文")
    word_count = Column(Integer, default=0)
    published = Column(Integer, default=0, comment="0=草稿 1=已推送")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
