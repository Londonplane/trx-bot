from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import UserBalanceResponse, UserBalanceDeductRequest, UserDepositRequest, ApiResponse
from app.services.user_service import UserService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/{user_id}/balance", response_model=UserBalanceResponse)
async def get_user_balance(user_id: int, db: Session = Depends(get_db)):
    """查询用户余额"""
    try:
        user_service = UserService(db)
        balance = user_service.get_user_balance(user_id)
        return balance
    except Exception as e:
        logger.error(f"查询用户余额失败: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误")

@router.post("/{user_id}/deduct", response_model=ApiResponse)
async def deduct_balance(user_id: int, request: UserBalanceDeductRequest, db: Session = Depends(get_db)):
    """扣减用户余额（下单时使用）"""
    try:
        user_service = UserService(db)
        success = user_service.deduct_balance(user_id, request.amount, request.order_id, request.description)
        if success:
            return ApiResponse(success=True, message="余额扣减成功")
        else:
            raise HTTPException(status_code=400, detail="余额不足")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"扣减余额失败: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误")

@router.post("/{user_id}/deposit", response_model=ApiResponse)
async def confirm_deposit(user_id: int, request: UserDepositRequest, db: Session = Depends(get_db)):
    """确认用户充值"""
    try:
        user_service = UserService(db)
        success = await user_service.confirm_deposit(user_id, request.tx_hash, request.amount, request.currency)
        if success:
            return ApiResponse(success=True, message="充值确认成功")
        else:
            raise HTTPException(status_code=400, detail="充值确认失败")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"确认充值失败: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误")

@router.post("/{user_id}/refund", response_model=ApiResponse)
async def refund_user(user_id: int, amount: float, order_id: str, reason: str = None, db: Session = Depends(get_db)):
    """退款给用户"""
    try:
        user_service = UserService(db)
        success = user_service.refund_balance(user_id, amount, order_id, reason)
        if success:
            return ApiResponse(success=True, message="退款成功")
        else:
            raise HTTPException(status_code=400, detail="退款失败")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"退款失败: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误")