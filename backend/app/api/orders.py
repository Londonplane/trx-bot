from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import CreateOrderRequest, OrderResponse, ApiResponse
from app.services.order_service import OrderService
from typing import List
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=OrderResponse)
async def create_order(order_request: CreateOrderRequest, db: Session = Depends(get_db)):
    """创建新订单"""
    try:
        order_service = OrderService(db)
        order = await order_service.create_order(order_request)
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建订单失败: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误")

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, db: Session = Depends(get_db)):
    """查询订单详情"""
    try:
        order_service = OrderService(db)
        order = order_service.get_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")
        return order
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询订单失败: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误")

@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    user_id: int = None, 
    status: str = None,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """获取订单列表（支持管理后台）"""
    try:
        order_service = OrderService(db)
        if user_id:
            # 获取指定用户的订单
            orders = order_service.get_user_orders(user_id, skip=skip, limit=limit)
        else:
            # 获取所有订单（管理后台用）
            orders = order_service.get_all_orders(status=status, skip=skip, limit=limit)
        return orders
    except Exception as e:
        logger.error(f"查询订单失败: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误")

@router.post("/{order_id}/cancel", response_model=ApiResponse)
async def cancel_order(order_id: str, db: Session = Depends(get_db)):
    """取消订单"""
    try:
        order_service = OrderService(db)
        success = await order_service.cancel_order(order_id)
        if success:
            return ApiResponse(success=True, message="订单已取消")
        else:
            raise HTTPException(status_code=400, detail="订单无法取消")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"取消订单失败: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误")