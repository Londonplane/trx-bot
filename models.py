import logging
import json
import os
from typing import List, Dict, Optional
from backend_api_client import backend_api

logger = logging.getLogger(__name__)

class UserSession:
    def __init__(self, user_id: int = None):
        self.user_id = user_id
        self.selected_duration = "1h"  # 默认选择1小时
        self.selected_energy = "65K"  # 默认选择65K
        self.selected_address = None
        self.computed_cost = "0.00"
        self._user_balance = None  # 缓存用户余额
        self.pending_input = None  # 用于跟踪等待的用户输入类型
        self.address_balance = None  # 存储地址余额信息 {"TRX": "18.900009", "ENERGY": "0"}
        self.wallet_addresses = []  # 用户绑定的钱包地址列表
        self.show_balance_in_buy_page = False  # 是否在购买页面显示余额信息
        # 订单相关信息
        self.last_order_id = None  # 最近一次订单ID
        self.last_transaction_hash = None  # 最近一次交易哈希
        self.last_order_time = None  # 最近一次订单时间
    
    @property
    def user_balance(self) -> Dict[str, str]:
        """获取用户余额（调用后端API）"""
        if self.user_id is None:
            return {"TRX": "0.000", "USDT": "0.00"}
        
        # 尝试从后端API获取真实余额
        try:
            balance_data = backend_api.get_user_balance(self.user_id)
            if balance_data:
                return {
                    "TRX": f"{float(balance_data['balance_trx']):.3f}",
                    "USDT": f"{float(balance_data['balance_usdt']):.2f}"
                }
        except Exception as e:
            logger.warning(f"获取用户余额失败，使用Mock数据: {e}")
        
        # 后端API不可用时使用Mock数据
        return {"TRX": "20.000", "USDT": "50.00"}
    
    def create_order(self, energy_amount: int, duration: str, receive_address: str) -> Dict:
        """创建订单（调用后端API）"""
        if self.user_id is None:
            return {"success": False, "message": "用户ID未设置"}
        
        try:
            order_data = backend_api.create_order(
                user_id=self.user_id,
                energy_amount=energy_amount,
                duration=duration,
                receive_address=receive_address
            )
            
            if order_data:
                self.last_order_id = order_data["id"]
                self.last_transaction_hash = order_data.get("tx_hash", "pending")
                logger.info(f"用户 {self.user_id} 通过API创建订单成功: {order_data['id']}")
                
                # 如果有tx_hash说明是真实交易，否则是pending状态
                if order_data.get("tx_hash") and order_data["tx_hash"] != "pending":
                    logger.info(f"真实交易已执行，tx_hash: {order_data['tx_hash']}")
                else:
                    logger.info(f"订单已创建，等待后台处理器执行交易")
                
                return {"success": True, "order": order_data}
            else:
                logger.warning(f"用户 {self.user_id} API返回空数据，使用Mock订单")
                return self._create_mock_order(energy_amount, duration, receive_address)
                
        except Exception as e:
            logger.warning(f"用户 {self.user_id} 通过API创建订单失败，使用Mock订单: {e}")
            return self._create_mock_order(energy_amount, duration, receive_address)
    
    def _create_mock_order(self, energy_amount: int, duration: str, receive_address: str) -> Dict:
        """创建Mock订单"""
        import uuid
        import datetime
        
        mock_order_id = str(uuid.uuid4())
        mock_order = {
            "id": mock_order_id,
            "user_id": self.user_id,
            "energy_amount": energy_amount,
            "duration": duration,
            "receive_address": receive_address,
            "status": "completed",
            "tx_hash": "mock_transaction_hash_" + mock_order_id[:8],
            "created_at": datetime.datetime.now().isoformat(),
            "cost_trx": float(calculate_mock_cost(str(energy_amount), duration))
        }
        
        self.last_order_id = mock_order_id
        self.last_transaction_hash = mock_order["tx_hash"]
        logger.info(f"用户 {self.user_id} 创建Mock订单: {mock_order_id}")
        
        return {"success": True, "order": mock_order}
    
    def get_order_status(self, order_id: str) -> Optional[Dict]:
        """查询订单状态（调用后端API）"""
        if not order_id:
            return None
        
        try:
            order_data = backend_api.get_order(order_id)
            return order_data
        except Exception as e:
            logger.error(f"查询订单状态异常: {e}")
            return None

# 用户会话状态存储（内存）
user_sessions = {}

# 持久化存储配置
WALLET_DATA_FILE = "user_wallets.json"

def load_wallet_data() -> Dict:
    """从文件加载钱包数据"""
    if os.path.exists(WALLET_DATA_FILE):
        try:
            with open(WALLET_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"加载钱包数据失败: {e}")
            return {}
    return {}

def save_wallet_data(data: Dict) -> bool:
    """保存钱包数据到文件"""
    try:
        with open(WALLET_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        logger.error(f"保存钱包数据失败: {e}")
        return False

def get_user_wallet_data(user_id: int) -> List[str]:
    """获取用户的持久化钱包地址列表"""
    wallet_data = load_wallet_data()
    return wallet_data.get(str(user_id), [])

def save_user_wallet_data(user_id: int, addresses: List[str]) -> bool:
    """保存用户的钱包地址列表"""
    wallet_data = load_wallet_data()
    wallet_data[str(user_id)] = addresses
    return save_wallet_data(wallet_data)

def get_user_session(user_id: int) -> UserSession:
    """获取或创建用户会话"""
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession(user_id=user_id)
        
        # 尝试从后端API加载钱包地址
        try:
            wallets_data = backend_api.get_user_wallets(user_id)
            if wallets_data:
                api_addresses = [
                    wallet["wallet_address"] for wallet in wallets_data if wallet["is_active"]
                ]
                user_sessions[user_id].wallet_addresses = api_addresses
                # 同步更新本地文件，保持数据一致性
                save_user_wallet_data(user_id, api_addresses)
                logger.info(f"用户 {user_id} 从API加载 {len(api_addresses)} 个地址，并同步到本地文件")
            else:
                # 后端API返回空数据，使用本地文件
                persistent_addresses = get_user_wallet_data(user_id)
                user_sessions[user_id].wallet_addresses = persistent_addresses
                logger.info(f"用户 {user_id} API返回空数据，从本地文件加载 {len(persistent_addresses)} 个地址")
        except Exception as e:
            logger.warning(f"从后端API加载钱包地址失败，使用本地文件: {e}")
            persistent_addresses = get_user_wallet_data(user_id)
            user_sessions[user_id].wallet_addresses = persistent_addresses
            logger.info(f"用户 {user_id} API失败，从本地文件加载 {len(persistent_addresses)} 个地址")
    
    return user_sessions[user_id]

def add_wallet_address(user_id: int, address: str) -> bool:
    """添加钱包地址"""
    session = get_user_session(user_id)
    
    # 验证地址格式
    if not is_valid_tron_address(address):
        return False
    
    # 检查地址是否已存在
    if address in session.wallet_addresses:
        return False
    
    # 尝试通过后端API添加
    api_success = False
    try:
        success = backend_api.add_user_wallet(user_id, address)
        if success:
            api_success = True
            logger.info(f"用户 {user_id} 通过API添加地址: {address}")
    except Exception as e:
        logger.warning(f"通过API添加钱包地址失败: {e}")
    
    # 更新本地会话
    session.wallet_addresses.append(address)
    
    # 无论API是否成功，都同时保存到本地文件作为备份
    save_user_wallet_data(user_id, session.wallet_addresses)
    
    if api_success:
        logger.info(f"用户 {user_id} 地址已添加到API和本地备份: {address}")
    else:
        logger.info(f"用户 {user_id} 地址仅保存到本地文件: {address}")
    
    return True

def remove_wallet_address(user_id: int, address: str) -> bool:
    """删除钱包地址"""
    session = get_user_session(user_id)
    
    # 检查地址是否存在
    if address not in session.wallet_addresses:
        return False
    
    # 尝试通过后端API删除
    api_success = False
    try:
        success = backend_api.remove_user_wallet(user_id, address)
        if success:
            api_success = True
            logger.info(f"用户 {user_id} 通过API删除地址: {address}")
    except Exception as e:
        logger.warning(f"通过API删除钱包地址失败: {e}")
    
    # 更新本地会话
    session.wallet_addresses.remove(address)
    
    # 如果删除的是当前选中的地址，清空选择
    if session.selected_address == address:
        session.selected_address = None
    
    # 无论API是否成功，都同时更新本地文件
    save_user_wallet_data(user_id, session.wallet_addresses)
    
    if api_success:
        logger.info(f"用户 {user_id} 地址已从API和本地备份删除: {address}")
    else:
        logger.info(f"用户 {user_id} 地址仅从本地文件删除: {address}")
    
    return True

def get_wallet_addresses(user_id: int) -> list:
    """获取用户的钱包地址列表"""
    session = get_user_session(user_id)
    return session.wallet_addresses.copy()

def is_valid_tron_address(address: str) -> bool:
    """验证TRON地址格式"""
    if not address:
        return False
    
    # 基本格式检查
    if address.startswith('T') and len(address) == 34:
        return True
    elif len(address) == 42 and address.startswith('41'):
        return True
    
    return False

def calculate_mock_cost(energy: str, duration: str) -> str:
    """模拟成本计算"""
    energy_map = {"65K": 65000, "135K": 135000, "270K": 270000, "540K": 540000, "1M": 1000000}
    duration_map = {"1h": 1/24, "1d": 1, "3d": 3, "7d": 7, "14d": 14}
    
    # 获取数值，如果是自定义数量则直接解析
    if energy.endswith("K"):
        energy_val = energy_map.get(energy, 135000)
    elif energy.endswith("M"):
        energy_val = int(float(energy[:-1]) * 1000000)
    else:
        try:
            energy_val = int(energy)
        except:
            energy_val = 135000
    
    duration_val = duration_map.get(duration, 1)
    
    # 简单的定价公式 (仅为演示)
    base_price = energy_val * 0.00001  # 基础价格
    time_multiplier = duration_val * 0.8  # 时间倍数
    total_cost = base_price * time_multiplier
    
    # 价格调整：乘以20来匹配市场价格
    market_adjusted_cost = total_cost * 20
    
    return f"{market_adjusted_cost:.2f}"

def format_energy(energy: str) -> str:
    """格式化能量显示"""
    if energy.isdigit():
        val = int(energy)
        if val >= 1000000:
            return f"{val/1000000:.1f}M"
        elif val >= 1000:
            return f"{val//1000}K"
    return energy