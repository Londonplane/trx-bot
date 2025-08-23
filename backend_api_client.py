import requests
import logging
from typing import Optional, Dict, List
from decimal import Decimal

logger = logging.getLogger(__name__)

class BackendAPIClient:
    """后端API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, data: dict = None) -> Optional[dict]:
        """发起API请求"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=data, timeout=10)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, timeout=10)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, timeout=10)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败 {method} {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"API调用异常: {e}")
            return None
    
    # 用户余额相关API
    def get_user_balance(self, user_id: int) -> Optional[Dict]:
        """获取用户余额"""
        return self._make_request("GET", f"/api/users/{user_id}/balance")
    
    def deduct_user_balance(self, user_id: int, amount: float, order_id: str, description: str = None) -> bool:
        """扣减用户余额"""
        data = {
            "amount": amount,
            "order_id": order_id,
            "description": description
        }
        result = self._make_request("POST", f"/api/users/{user_id}/deduct", data)
        return result and result.get("success", False)
    
    def confirm_user_deposit(self, user_id: int, tx_hash: str, amount: float, currency: str) -> bool:
        """确认用户充值"""
        data = {
            "tx_hash": tx_hash,
            "amount": amount,
            "currency": currency
        }
        result = self._make_request("POST", f"/api/users/{user_id}/deposit", data)
        return result and result.get("success", False)
    
    # 订单相关API
    def create_order(self, user_id: int, energy_amount: int, duration: str, receive_address: str) -> Optional[Dict]:
        """创建订单"""
        data = {
            "user_id": user_id,
            "energy_amount": energy_amount,
            "duration": duration,
            "receive_address": receive_address
        }
        return self._make_request("POST", "/api/orders", data)
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """查询订单详情"""
        return self._make_request("GET", f"/api/orders/{order_id}")
    
    def get_user_orders(self, user_id: int, limit: int = 10) -> List[Dict]:
        """获取用户订单列表"""
        result = self._make_request("GET", "/api/orders", {"user_id": user_id, "limit": limit})
        return result if result else []
    
    def cancel_order(self, order_id: str) -> bool:
        """取消订单"""
        result = self._make_request("POST", f"/api/orders/{order_id}/cancel")
        return result and result.get("success", False)
    
    # 钱包相关API
    def get_user_wallets(self, user_id: int) -> List[Dict]:
        """获取用户钱包列表"""
        result = self._make_request("GET", f"/api/wallets/users/{user_id}")
        return result if result else []
    
    def add_user_wallet(self, user_id: int, wallet_address: str) -> bool:
        """添加用户钱包地址"""
        data = {"wallet_address": wallet_address}
        result = self._make_request("POST", f"/api/wallets/users/{user_id}", data)
        return result and result.get("success", False)
    
    def remove_user_wallet(self, user_id: int, wallet_address: str) -> bool:
        """删除用户钱包地址"""
        result = self._make_request("DELETE", f"/api/wallets/users/{user_id}/{wallet_address}")
        return result and result.get("success", False)

# 全局API客户端实例
backend_api = BackendAPIClient()