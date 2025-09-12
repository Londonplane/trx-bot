#!/usr/bin/env python3
"""
测试用户余额充值脚本
直接操作数据库为测试用户增加余额
"""
import sys
import os

# 设置路径以导入后端模块
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.database import SessionLocal
from backend.app.models import User, BalanceTransaction
from decimal import Decimal
from datetime import datetime

def charge_test_user_balance():
    """为测试用户充值余额"""
    user_id = 123456
    charge_amount = Decimal("10.0")
    
    db = SessionLocal()
    try:
        # 获取或创建用户
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(id=user_id, balance_trx=Decimal("0"))
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # 记录充值前余额
        balance_before = user.balance_trx
        
        # 增加余额
        user.balance_trx += charge_amount
        
        # 创建余额变动记录
        transaction = BalanceTransaction(
            user_id=user_id,
            transaction_type="deposit",
            amount=charge_amount,
            balance_after=user.balance_trx,
            reference_id="test-charge-001",
            description="测试环境余额充值"
        )
        db.add(transaction)
        
        # 提交事务
        db.commit()
        
        print(f"用户 {user_id} 余额充值成功!")
        print(f"充值前余额: {balance_before} TRX")
        print(f"充值金额: {charge_amount} TRX")
        print(f"充值后余额: {user.balance_trx} TRX")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"充值失败: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("开始为测试用户充值余额...")
    success = charge_test_user_balance()
    if success:
        print("测试用户余额充值完成!")
    else:
        print("充值失败，请检查错误信息")