import logging

logger = logging.getLogger(__name__)

class UserSession:
    def __init__(self):
        self.selected_duration = "1d"  # 默认选择1天
        self.selected_energy = "135K"  # 默认选择135K
        self.selected_address = None
        self.computed_cost = "0.00"
        self.user_balance = {"TRX": "100.00", "USDT": "50.00"}  # Mock数据
        self.pending_input = None  # 用于跟踪等待的用户输入类型

# 用户会话状态存储
user_sessions = {}

def get_user_session(user_id: int) -> UserSession:
    """获取或创建用户会话"""
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession()
    return user_sessions[user_id]

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