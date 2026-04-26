import logging
import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import init_db
from app.api import daily_review, trade, socratic, daily_plan, dashboard, snapshot, strategy

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("启动中，初始化数据库...")
    await init_db()
    logger.info("数据库初始化完成")
    yield


app = FastAPI(
    title="TradeReview Pro API",
    description="AI增强交易复盘系统",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(daily_review.router)
app.include_router(trade.router)
app.include_router(socratic.router)
app.include_router(daily_plan.router)
app.include_router(dashboard.router)
app.include_router(snapshot.router)
app.include_router(strategy.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    logger.error(f"未捕获异常\n路径: {request.url}\n{tb}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "traceback": tb},
    )


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}