from sqlalchemy import Column, Integer, BigInteger, String, DECIMAL, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid

class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True)  # Telegram用户ID
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    balance_trx = Column(DECIMAL(18, 6), default=0)
    balance_usdt = Column(DECIMAL(18, 6), default=0)
    total_orders = Column(Integer, default=0)
    total_spent = Column(DECIMAL(18, 6), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    wallets = relationship("UserWallet", back_populates="user")
    orders = relationship("Order", back_populates="user")
    balance_transactions = relationship("BalanceTransaction", back_populates="user")

class UserWallet(Base):
    """用户钱包地址表"""
    __tablename__ = "user_wallets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    wallet_address = Column(String(42), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联关系
    user = relationship("User", back_populates="wallets")

class Order(Base):
    """订单表"""
    __tablename__ = "orders"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(BigInteger, ForeignKey("users.id"))
    receive_address = Column(String(42), nullable=False)
    energy_amount = Column(Integer, nullable=False)
    duration_hours = Column(Integer, nullable=False)
    cost_trx = Column(DECIMAL(18, 6), nullable=False)
    status = Column(String(20), default="pending")  # pending/processing/completed/failed/cancelled
    supplier_wallet = Column(String(42))
    tx_hash = Column(String(66))
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # 关联关系
    user = relationship("User", back_populates="orders")

class BalanceTransaction(Base):
    """余额变动记录表"""
    __tablename__ = "balance_transactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    transaction_type = Column(String(20), nullable=False)  # deposit/deduct/refund
    amount = Column(DECIMAL(18, 6), nullable=False)
    balance_after = Column(DECIMAL(18, 6), nullable=False)
    reference_id = Column(String(255))  # 关联的订单ID或充值交易哈希
    description = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联关系
    user = relationship("User", back_populates="balance_transactions")

class SupplierWallet(Base):
    """供应商钱包池表"""
    __tablename__ = "supplier_wallets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    wallet_address = Column(String(42), unique=True, nullable=False)
    private_key_encrypted = Column(Text, nullable=False)  # 加密存储的私钥
    trx_balance = Column(DECIMAL(18, 6), default=0)
    energy_available = Column(Integer, default=0)
    energy_limit = Column(Integer, default=0)
    bandwidth_available = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    last_balance_check = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())