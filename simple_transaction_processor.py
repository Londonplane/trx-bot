#!/usr/bin/env python3
"""
简化的交易处理器
立即处理pending订单，无需Redis/Celery
"""
import sys
import os
sys.path.append('backend')

import asyncio
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.models import Order
from backend.app.services.tron_service import TronTransactionService

# 数据库连接
DATABASE_URL = "sqlite:///backend/trx_energy.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def process_pending_orders():
    """处理所有pending状态的订单"""
    db = SessionLocal()
    try:
        # 设置环境变量
        if os.path.exists('.env.test'):
            with open('.env.test', 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
        
        # 创建交易服务
        tron_service = TronTransactionService(db)
        
        # 查找所有pending订单
        pending_orders = db.query(Order).filter(Order.status == "pending").all()
        
        print(f"Found {len(pending_orders)} pending orders to process")
        
        for order in pending_orders:
            print(f"\nProcessing order: {order.id}")
            print(f"User: {order.user_id}")
            print(f"Energy: {order.energy_amount}")
            print(f"Address: {order.receive_address}")
            
            try:
                # 执行能量委托
                success = await tron_service.execute_energy_delegate(order.id)
                
                if success:
                    print(f"SUCCESS: Order {order.id} processed successfully")
                    
                    # 重新查询订单获取最新状态
                    updated_order = db.query(Order).filter(Order.id == order.id).first()
                    if updated_order and updated_order.tx_hash:
                        print(f"Transaction hash: {updated_order.tx_hash}")
                        print(f"View on Shasta: https://shasta.tronscan.org/#/transaction/{updated_order.tx_hash}")
                else:
                    print(f"ERROR: Failed to process order {order.id}")
                    
            except Exception as e:
                print(f"ERROR processing order {order.id}: {e}")
                
            # 等待一下再处理下一个订单
            await asyncio.sleep(1)
            
    finally:
        db.close()

async def main():
    print("Simple Transaction Processor")
    print("=" * 40)
    
    while True:
        try:
            await process_pending_orders()
            
            print(f"\nWaiting 10 seconds before next check...")
            await asyncio.sleep(10)
            
        except KeyboardInterrupt:
            print("\nStopping transaction processor...")
            break
        except Exception as e:
            print(f"ERROR in main loop: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())