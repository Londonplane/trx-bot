from sqlalchemy.orm import Session
from app.models import User, BalanceTransaction
from app.schemas import UserBalanceResponse
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_balance(self, user_id: int) -> UserBalanceResponse:
        """获取用户余额"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            # 创建新用户
            user = User(id=user_id)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        
        return UserBalanceResponse(
            user_id=user.id,
            balance_trx=user.balance_trx,
            balance_usdt=user.balance_usdt
        )
    
    def deduct_balance(self, user_id: int, amount: Decimal, order_id: str, description: str = None) -> bool:
        """扣减用户余额"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or user.balance_trx < amount:
            return False
        
        # 扣减余额
        user.balance_trx -= amount
        user.total_spent += amount
        
        # 记录余额变动
        transaction = BalanceTransaction(
            user_id=user_id,
            transaction_type="deduct",
            amount=-amount,  # 负数表示扣减
            balance_after=user.balance_trx,
            reference_id=order_id,
            description=description or f"订单扣费: {order_id}"
        )
        
        self.db.add(transaction)
        self.db.commit()
        
        logger.info(f"用户 {user_id} 余额扣减 {amount} TRX，订单: {order_id}")
        return True
    
    async def confirm_deposit(self, user_id: int, tx_hash: str, amount: Decimal, currency: str) -> bool:
        """确认用户充值"""
        # 检查充值是否已处理
        existing_tx = self.db.query(BalanceTransaction).filter(
            BalanceTransaction.reference_id == tx_hash
        ).first()
        if existing_tx:
            return False  # 充值已处理
        
        # 获取或创建用户
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(id=user_id)
            self.db.add(user)
            self.db.flush()
        
        # 转换为TRX（如果是USDT）
        if currency.upper() == "USDT":
            # USDT转TRX汇率 (1 TRX = 0.38826 USDT)
            trx_amount = amount / Decimal("0.38826")
        else:
            trx_amount = amount
        
        # 增加余额
        user.balance_trx += trx_amount
        
        # 记录充值
        transaction = BalanceTransaction(
            user_id=user_id,
            transaction_type="deposit",
            amount=trx_amount,
            balance_after=user.balance_trx,
            reference_id=tx_hash,
            description=f"{currency}充值: {amount} -> {trx_amount} TRX"
        )
        
        self.db.add(transaction)
        self.db.commit()
        
        logger.info(f"用户 {user_id} 充值确认: {amount} {currency} -> {trx_amount} TRX")
        return True
    
    def refund_balance(self, user_id: int, amount: Decimal, order_id: str, reason: str = None) -> bool:
        """退款给用户"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # 增加余额
        user.balance_trx += amount
        
        # 记录退款
        transaction = BalanceTransaction(
            user_id=user_id,
            transaction_type="refund",
            amount=amount,
            balance_after=user.balance_trx,
            reference_id=order_id,
            description=reason or f"订单退款: {order_id}"
        )
        
        self.db.add(transaction)
        self.db.commit()
        
        logger.info(f"用户 {user_id} 退款: {amount} TRX，原因: {reason}")
        return True