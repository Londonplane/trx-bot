#!/usr/bin/env python3
"""
后端数据库初始化和用户充值
"""
import os
import sys

# 确保在后端目录内
os.chdir(os.path.dirname(__file__))

from app.database import engine, Base, SessionLocal
from app.models import User, BalanceTransaction
from decimal import Decimal

def init_db_and_charge():
    """初始化数据库并为测试用户充值"""
    # 1. 创建所有表
    print("创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")
    
    # 2. 为测试用户充值
    user_id = 123456
    charge_amount = Decimal("10.0")
    
    db = SessionLocal()
    try:
        # 获取或创建用户
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(
                id=user_id,
                username="test_user",
                balance_trx=Decimal("0")
            )
            db.add(user)
            print(f"创建新测试用户: {user_id}")
        
        balance_before = user.balance_trx
        user.balance_trx += charge_amount
        
        # 创建余额记录
        transaction = BalanceTransaction(
            user_id=user_id,
            transaction_type="deposit",
            amount=charge_amount,
            balance_after=user.balance_trx,
            reference_id="test-init-charge",
            description="测试初始化充值"
        )
        db.add(transaction)
        
        db.commit()
        
        print("用户充值完成:")
        print(f"  用户ID: {user_id}")
        print(f"  充值前: {balance_before} TRX")
        print(f"  充值后: {user.balance_trx} TRX")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"操作失败: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=== 后端数据库初始化 ===")
    success = init_db_and_charge()
    
    if success:
        print("初始化完成! 测试用户已准备就绪.")
    else:
        print("初始化失败!")