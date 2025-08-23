import logging
import json
import os
from typing import List, Dict

logger = logging.getLogger(__name__)

class UserSession:
    def __init__(self):
        self.selected_duration = "1h"  # 默认选择1小时
        self.selected_energy = "65K"  # 默认选择65K
        self.selected_address = None
        self.computed_cost = "0.00"
        self.user_balance = {"TRX": "20.000", "USDT": "50.00"}  # Mock数据
        self.pending_input = None  # 用于跟踪等待的用户输入类型
        self.address_balance = None  # 存储地址余额信息 {"TRX": "18.900009", "ENERGY": "0"}
        self.wallet_addresses = []  # 用户绑定的钱包地址列表
        self.show_balance_in_buy_page = False  # 是否在购买页面显示余额信息
        # 订单相关信息
        self.last_order_id = None  # 最近一次订单ID
        self.last_transaction_hash = None  # 最近一次交易哈希
        self.last_order_time = None  # 最近一次订单时间

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
        user_sessions[user_id] = UserSession()
        # 从持久化存储加载钱包地址
        persistent_addresses = get_user_wallet_data(user_id)
        user_sessions[user_id].wallet_addresses = persistent_addresses
    return user_sessions[user_id]

def add_wallet_address(user_id: int, address: str) -> bool:
    """添加钱包地址"""
    session = get_user_session(user_id)
    
    # 验证地址格式
    if not is_valid_tron_address(address):
        return False
    
    # 检查是否已存在
    if address not in session.wallet_addresses:
        session.wallet_addresses.append(address)
        # 保存到持久化存储
        save_user_wallet_data(user_id, session.wallet_addresses)
        logger.info(f"用户 {user_id} 添加地址: {address}")
        return True
    return False

def remove_wallet_address(user_id: int, address: str) -> bool:
    """删除钱包地址"""
    session = get_user_session(user_id)
    if address in session.wallet_addresses:
        session.wallet_addresses.remove(address)
        # 如果删除的是当前选中的地址，清空选择
        if session.selected_address == address:
            session.selected_address = None
        # 保存到持久化存储
        save_user_wallet_data(user_id, session.wallet_addresses)
        logger.info(f"用户 {user_id} 删除地址: {address}")
        return True
    return False

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
    
    return f"{total_cost:.2f}"

def format_energy(energy: str) -> str:
    """格式化能量显示"""
    if energy.isdigit():
        val = int(energy)
        if val >= 1000000:
            return f"{val/1000000:.1f}M"
        elif val >= 1000:
            return f"{val//1000}K"
    return energy