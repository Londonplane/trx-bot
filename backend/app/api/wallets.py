from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import AddWalletRequest, UserWalletResponse, ApiResponse
from app.services.wallet_service import WalletService
from typing import List
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/users/{user_id}", response_model=List[UserWalletResponse])
async def get_user_wallets(user_id: int, db: Session = Depends(get_db)):
    """获取用户钱包地址列表"""
    try:
        wallet_service = WalletService(db)
        wallets = wallet_service.get_user_wallets(user_id)
        return wallets
    except Exception as e:
        logger.error(f"查询用户钱包失败: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误")

@router.post("/users/{user_id}", response_model=ApiResponse)
async def add_user_wallet(user_id: int, request: AddWalletRequest, db: Session = Depends(get_db)):
    """添加用户钱包地址"""
    try:
        wallet_service = WalletService(db)
        success = wallet_service.add_user_wallet(user_id, request.wallet_address)
        if success:
            return ApiResponse(success=True, message="钱包地址添加成功")
        else:
            return ApiResponse(success=False, message="钱包地址已存在")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"添加钱包地址失败: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误")

@router.delete("/users/{user_id}/{wallet_address}", response_model=ApiResponse)
async def remove_user_wallet(user_id: int, wallet_address: str, db: Session = Depends(get_db)):
    """删除用户钱包地址"""
    try:
        wallet_service = WalletService(db)
        success = wallet_service.remove_user_wallet(user_id, wallet_address)
        if success:
            return ApiResponse(success=True, message="钱包地址删除成功")
        else:
            raise HTTPException(status_code=404, detail="钱包地址不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除钱包地址失败: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误")