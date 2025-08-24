from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.tron_service import TronTransactionService
from app.models import SupplierWallet
from pydantic import BaseModel
from typing import List
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class AddWalletRequest(BaseModel):
    private_key: str

class WalletResponse(BaseModel):
    id: int
    wallet_address: str
    trx_balance: str
    energy_available: int
    energy_limit: int
    is_active: bool
    last_balance_check: str = None

@router.post("/add", response_model=WalletResponse)
async def add_supplier_wallet(
    request: AddWalletRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """添加供应商钱包到钱包池"""
    try:
        tron_service = TronTransactionService(db)
        wallet = await tron_service.add_supplier_wallet(request.private_key)
        
        return WalletResponse(
            id=wallet.id,
            wallet_address=wallet.wallet_address,
            trx_balance=str(wallet.trx_balance),
            energy_available=wallet.energy_available,
            energy_limit=wallet.energy_limit,
            is_active=wallet.is_active,
            last_balance_check=wallet.last_balance_check.isoformat() if wallet.last_balance_check else None
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"添加供应商钱包失败: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")

@router.get("/", response_model=List[WalletResponse])
async def get_supplier_wallets(db: Session = Depends(get_db)):
    """获取所有供应商钱包列表"""
    wallets = db.query(SupplierWallet).all()
    
    return [WalletResponse(
        id=wallet.id,
        wallet_address=wallet.wallet_address,
        trx_balance=str(wallet.trx_balance),
        energy_available=wallet.energy_available,
        energy_limit=wallet.energy_limit,
        is_active=wallet.is_active,
        last_balance_check=wallet.last_balance_check.isoformat() if wallet.last_balance_check else None
    ) for wallet in wallets]

@router.post("/update-balances")
async def update_wallet_balances(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """更新所有供应商钱包余额"""
    def update_task():
        tron_service = TronTransactionService(db)
        asyncio.run(tron_service.update_wallet_balances())
    
    background_tasks.add_task(update_task)
    return {"message": "余额更新任务已启动"}

@router.post("/process-orders")
async def process_pending_orders(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """手动处理待处理订单"""
    def process_task():
        tron_service = TronTransactionService(db)
        asyncio.run(tron_service.process_pending_orders())
    
    background_tasks.add_task(process_task)
    return {"message": "订单处理任务已启动"}

@router.put("/{wallet_id}/toggle")
async def toggle_wallet_status(wallet_id: int, db: Session = Depends(get_db)):
    """启用/禁用供应商钱包"""
    wallet = db.query(SupplierWallet).filter(SupplierWallet.id == wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="钱包不存在")
    
    wallet.is_active = not wallet.is_active
    db.commit()
    
    return {"message": f"钱包{'启用' if wallet.is_active else '禁用'}成功"}

import asyncio