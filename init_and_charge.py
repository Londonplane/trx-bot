#!/usr/bin/env python3
"""
数据库初始化和用户余额充值工具
"""
import sys
import os

# 设置路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.database import engine, Base, SessionLocal
from backend.app.models import User, BalanceTransaction
from decimal import Decimal

def init_database():
    """初始化数据库表"""
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成!")

def charge_user_balance(user_id: int, amount: float):
    """为指定用户充值"""
    db = SessionLocal()
    try:
        # 获取或创建用户
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(id=user_id, balance_trx=Decimal("0"))
            db.add(user)
            print(f"创建新用户: {user_id}")
        
        balance_before = user.balance_trx
        user.balance_trx += Decimal(str(amount))
        
        # 创建余额变动记录
        transaction = BalanceTransaction(
            user_id=user_id,
            transaction_type="deposit", 
            amount=Decimal(str(amount)),
            balance_after=user.balance_trx,
            reference_id="test-charge",
            description="测试环境充值"
        )
        db.add(transaction)
        
        db.commit()
        
        print(f"用户 {user_id} 充值成功:")
        print(f"  充值前: {balance_before} TRX")
        print(f"  充值额: {amount} TRX") 
        print(f"  充值后: {user.balance_trx} TRX")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"充值失败: {e}")
        return False
    finally:
        db.close()

def main():
    print("=== 数据库初始化和用户充值工具 ===")
    
    # 1. 初始化数据库
    init_database()
    
    # 2. 为测试用户充值
    test_user_id = 123456
    charge_amount = 10.0
    
    print(f"\n为测试用户 {test_user_id} 充值 {charge_amount} TRX...")
    success = charge_user_balance(test_user_id, charge_amount)
    
    if success:
        print("\n充值完成! 现在可以开始测试了。")
    else:
        print("\n充值失败! 请检查错误信息。")

if __name__ == "__main__":
    main()