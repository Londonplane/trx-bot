"""
工作任务启动器 - 安全的任务调度接口
负责安全地启动后台任务，避免Redis连接错误影响主要业务逻辑
"""
import logging
import os

logger = logging.getLogger(__name__)

def safely_start_order_task(order_id: str) -> bool:
    """
    安全地启动订单处理任务
    
    Args:
        order_id: 订单ID
        
    Returns:
        bool: 是否成功启动后台任务
    """
    # 检查是否启用了后台任务
    if os.getenv("ENABLE_BACKGROUND_TASKS", "false").lower() != "true":
        logger.info(f"后台任务未启用，订单 {order_id} 将通过定时任务处理")
        return False
    
    try:
        # 先检查Redis连接
        import redis
        from app.database import settings
        
        redis_client = redis.Redis.from_url(settings.redis_url)
        redis_client.ping()  # 测试连接
        logger.info("Redis连接测试成功")
        
        # 成功连接Redis后，导入并启动Celery任务
        from tron_worker import execute_order
        execute_order.delay(order_id)
        logger.info(f"订单后台处理任务已启动: {order_id}")
        return True
        
    except ImportError as e:
        logger.warning(f"缺少依赖模块: {e}")
        return False
    except Exception as e:
        logger.warning(f"后台任务启动失败: {e}")
        return False

def is_background_tasks_available() -> bool:
    """检查后台任务是否可用"""
    try:
        import redis
        from app.database import settings
        
        redis_client = redis.Redis.from_url(settings.redis_url)
        redis_client.ping()
        return True
    except:
        return False