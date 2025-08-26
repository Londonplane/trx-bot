from sqlalchemy.orm import Session
from app.models import Order, User, BalanceTransaction
from app.schemas import CreateOrderRequest, OrderResponse
from decimal import Decimal
from datetime import datetime, timedelta
import logging
import uuid

logger = logging.getLogger(__name__)

class OrderService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_order(self, order_request: CreateOrderRequest) -> OrderResponse:
        """创建新订单"""
        # 验证用户存在
        user = self.db.query(User).filter(User.id == order_request.user_id).first()
        if not user:
            # 创建新用户
            user = User(id=order_request.user_id)
            self.db.add(user)
            self.db.commit()
        
        # 计算订单费用
        cost = self._calculate_cost(order_request.energy_amount, order_request.duration)
        
        # 检查用户余额
        if user.balance_trx < cost:
            raise ValueError(f"余额不足：需要 {cost} TRX，当前余额 {user.balance_trx} TRX")
        
        # 转换duration为小时数
        duration_hours = self._parse_duration(order_request.duration)
        
        # 创建订单
        order = Order(
            id=str(uuid.uuid4()),
            user_id=order_request.user_id,
            receive_address=order_request.receive_address,
            energy_amount=order_request.energy_amount,
            duration_hours=duration_hours,
            cost_trx=cost,
            expires_at=datetime.utcnow() + timedelta(minutes=30)  # 30分钟后过期
        )
        
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        
        # 触发后台任务立即处理订单（如果Celery可用）
        try:
            from tron_worker import execute_order
            execute_order.delay(order.id)
            logger.info(f"订单后台处理任务已启动: {order.id}")
        except ImportError:
            logger.warning("Celery不可用，订单将通过定时任务处理")
        
        logger.info(f"订单创建成功: {order.id}, 用户: {order_request.user_id}")
        return self._order_to_response(order)
    
    def get_order(self, order_id: str) -> OrderResponse:
        """查询订单详情"""
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return None
        return self._order_to_response(order)
    
    def get_user_orders(self, user_id: int, skip: int = 0, limit: int = 100) -> list[OrderResponse]:
        """获取用户订单列表"""
        orders = self.db.query(Order).filter(
            Order.user_id == user_id
        ).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
        
        return [self._order_to_response(order) for order in orders]
    
    def get_all_orders(self, status: str = None, skip: int = 0, limit: int = 100) -> list[OrderResponse]:
        """获取所有订单列表（管理后台用）"""
        query = self.db.query(Order)
        
        if status:
            query = query.filter(Order.status == status)
        
        orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
        return [self._order_to_response(order) for order in orders]
    
    async def cancel_order(self, order_id: str) -> bool:
        """取消订单"""
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return False
        
        if order.status not in ["pending", "processing"]:
            return False
        
        # 如果已扣减余额，需要退款
        if order.status == "processing":
            user = self.db.query(User).filter(User.id == order.user_id).first()
            if user:
                user.balance_trx += order.cost_trx
                
                # 记录退款
                refund_tx = BalanceTransaction(
                    user_id=order.user_id,
                    transaction_type="refund",
                    amount=order.cost_trx,
                    balance_after=user.balance_trx,
                    reference_id=order.id,
                    description="订单取消退款"
                )
                self.db.add(refund_tx)
        
        order.status = "cancelled"
        self.db.commit()
        
        logger.info(f"订单取消成功: {order_id}")
        return True
    
    def _calculate_cost(self, energy_amount: int, duration: str) -> Decimal:
        """计算订单费用"""
        # 基础定价策略
        duration_map = {"1h": 1/24, "1d": 1, "3d": 3, "7d": 7, "14d": 14}
        duration_val = duration_map.get(duration, 1)
        
        base_price = Decimal(energy_amount) * Decimal("0.00001")  # 基础价格
        time_multiplier = Decimal(str(duration_val * 0.8))        # 时间倍数
        total_cost = base_price * time_multiplier
        
        return round(total_cost, 6)
    
    def _parse_duration(self, duration: str) -> int:
        """解析duration为小时数"""
        duration_map = {"1h": 1, "1d": 24, "3d": 72, "7d": 168, "14d": 336}
        return duration_map.get(duration, 24)
    
    def _order_to_response(self, order: Order) -> OrderResponse:
        """转换订单模型为响应格式"""
        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            receive_address=order.receive_address,
            energy_amount=order.energy_amount,
            duration_hours=order.duration_hours,
            cost_trx=order.cost_trx,
            status=order.status,
            supplier_wallet=order.supplier_wallet,
            tx_hash=order.tx_hash,
            error_message=order.error_message,
            created_at=order.created_at,
            completed_at=order.completed_at
        )