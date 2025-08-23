from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    DEDUCT = "deduct"
    REFUND = "refund"

# 请求模型
class CreateOrderRequest(BaseModel):
    user_id: int
    energy_amount: int = Field(..., ge=1000, le=10000000, description="能量数量")
    duration: str = Field(..., description="租用时长：1h/1d/3d/7d/14d")
    receive_address: str = Field(..., min_length=34, max_length=42, description="接收地址")

class UserBalanceDeductRequest(BaseModel):
    amount: Decimal = Field(..., gt=0, description="扣减金额")
    order_id: str = Field(..., description="关联订单ID")
    description: Optional[str] = None

class UserDepositRequest(BaseModel):
    tx_hash: str = Field(..., min_length=64, max_length=66, description="充值交易哈希")
    amount: Decimal = Field(..., gt=0, description="充值金额")
    currency: str = Field(..., description="充值币种：TRX/USDT")

class AddWalletRequest(BaseModel):
    wallet_address: str = Field(..., min_length=34, max_length=42, description="TRON地址")

# 响应模型
class UserBalanceResponse(BaseModel):
    user_id: int
    balance_trx: Decimal
    balance_usdt: Decimal

class OrderResponse(BaseModel):
    id: str
    user_id: int
    receive_address: str
    energy_amount: int
    duration_hours: int
    cost_trx: Decimal
    status: OrderStatus
    supplier_wallet: Optional[str] = None
    tx_hash: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

class UserWalletResponse(BaseModel):
    id: int
    wallet_address: str
    is_active: bool
    created_at: datetime

class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None