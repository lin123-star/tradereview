import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.socratic import (
    StartSessionRequest, ReplyRequest, ReplyResponse, SessionOut
)
from app.services.socratic_service import SocraticService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/socratic", tags=["AI审讯室"])


@router.post("/start", response_model=SessionOut)
async def start_session(req: StartSessionRequest, db: AsyncSession = Depends(get_db)):
    """开始或继续审讯，返回会话信息和AI首问"""
    try:
        session, ai_question = await SocraticService.start(db, req.trade_id)
        return session
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"启动审讯失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reply", response_model=ReplyResponse)
async def reply(req: ReplyRequest, db: AsyncSession = Depends(get_db)):
    """用户回答后AI继续追问"""
    try:
        result = await SocraticService.reply(db, req.session_id, req.user_message)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"审讯追问失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trade/{trade_id}", response_model=list[SessionOut])
async def get_trade_sessions(trade_id: int, db: AsyncSession = Depends(get_db)):
    """获取某笔交易的所有审讯会话"""
    return await SocraticService.get_sessions_by_trade(db, trade_id)


@router.get("/session/{session_id}", response_model=SessionOut)
async def get_session(session_id: int, db: AsyncSession = Depends(get_db)):
    """获取单个审讯会话详情"""
    session = await SocraticService.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="审讯会话不存在")
    return session
