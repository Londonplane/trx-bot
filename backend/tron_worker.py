from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import settings
from app.services.tron_service import TronTransactionService
import asyncio
import logging
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Celery应用
celery_app = Celery(
    "tron_worker",
    broker=settings.redis_url,
    backend=settings.redis_url
)

# 配置Celery
celery_app.conf.update(
    task_routes={
        'tron_worker.process_orders': {'queue': 'orders'},
        'tron_worker.update_wallets': {'queue': 'wallets'},
    },
    beat_schedule={
        'process-orders-every-30-seconds': {
            'task': 'tron_worker.process_orders',
            'schedule': 30.0,  # 每30秒执行一次
        },
        'update-wallets-every-5-minutes': {
            'task': 'tron_worker.update_wallets',
            'schedule': 300.0,  # 每5分钟执行一次
        },
    },
    timezone='UTC',
)

# 数据库连接
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@celery_app.task(name="tron_worker.process_orders")
def process_orders():
    """处理待处理订单的后台任务"""
    db = SessionLocal()
    try:
        tron_service = TronTransactionService(db)
        
        # 运行异步任务
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(tron_service.process_pending_orders())
        loop.close()
        
        logger.info("订单处理任务完成")
        return "订单处理完成"
    
    except Exception as e:
        logger.error(f"订单处理任务失败: {str(e)}")
        raise
    
    finally:
        db.close()

@celery_app.task(name="tron_worker.update_wallets")
def update_wallets():
    """更新供应商钱包余额的后台任务"""
    db = SessionLocal()
    try:
        tron_service = TronTransactionService(db)
        
        # 运行异步任务
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(tron_service.update_wallet_balances())
        loop.close()
        
        logger.info("钱包余额更新任务完成")
        return "钱包余额更新完成"
    
    except Exception as e:
        logger.error(f"钱包余额更新任务失败: {str(e)}")
        raise
    
    finally:
        db.close()

@celery_app.task(name="tron_worker.execute_order")
def execute_order(order_id: str):
    """执行单个订单的后台任务"""
    db = SessionLocal()
    try:
        tron_service = TronTransactionService(db)
        
        # 运行异步任务
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(tron_service.execute_energy_delegate(order_id))
        loop.close()
        
        logger.info(f"订单执行完成: {order_id}, 结果: {result}")
        return f"订单 {order_id} 执行{'成功' if result else '失败'}"
    
    except Exception as e:
        logger.error(f"订单执行失败: {order_id}, 错误: {str(e)}")
        raise
    
    finally:
        db.close()

if __name__ == "__main__":
    # 启动Celery Worker
    celery_app.start()