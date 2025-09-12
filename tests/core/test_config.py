"""
测试配置和常量定义

这个模块包含了所有测试的全局配置和常量，
确保测试环境的一致性和可维护性。
"""

import os
from typing import Dict, Any

# 测试环境配置
TEST_CONFIG = {
    # 网络配置
    "TRON_NETWORK": "shasta",  # 统一使用Shasta测试网
    "BACKEND_URL": "http://localhost:8002",
    "API_TIMEOUT": 10,
    
    # 测试用户配置
    "TEST_USER_ID": "test_user_12345",
    "TEST_CHAT_ID": "test_chat_67890",
    
    # 测试数据配置
    "MOCK_DATA_ENABLED": True,
    "API_RETRY_COUNT": 3,
    "BALANCE_TOLERANCE": 1.0,  # TRX余额允许的误差范围
    
    # 测试结果配置
    "SAVE_TEST_RESULTS": True,
    "RESULTS_DIR": "tests/results",
    "ENABLE_DETAILED_LOGS": True
}

# 能量租赁测试参数
ENERGY_TEST_PARAMS = {
    "energy_amounts": [65000, 135000, 270000, 540000, 1000000],
    "durations": ["1h", "1d", "3d", "7d", "14d"],
    "default_test_order": {
        "energy_amount": 135000,
        "duration": "1d"
    }
}

# Mock数据定义
MOCK_COST_CALCULATION = {
    "base_rate": 0.000045,  # 每单位能量的基础价格(TRX)
    "duration_multipliers": {
        "1h": 1.0,
        "1d": 0.8, 
        "3d": 0.7,
        "7d": 0.6,
        "14d": 0.5
    }
}

# API端点配置
API_ENDPOINTS = {
    "health_check": "/health",
    "user_balance": "/api/users/{user_id}/balance",
    "user_wallets": "/api/users/{user_id}/wallets",
    "create_order": "/api/orders"
}

def get_test_config(key: str, default: Any = None) -> Any:
    """获取测试配置值"""
    return TEST_CONFIG.get(key, default)

def get_backend_url() -> str:
    """获取后端服务URL"""
    return get_test_config("BACKEND_URL")

def get_api_endpoint(endpoint_name: str, **kwargs) -> str:
    """获取完整的API端点URL"""
    endpoint = API_ENDPOINTS.get(endpoint_name)
    if endpoint and kwargs:
        endpoint = endpoint.format(**kwargs)
    return f"{get_backend_url()}{endpoint}"

def calculate_mock_cost(energy_amount: int, duration: str) -> float:
    """计算Mock订单成本"""
    base_rate = MOCK_COST_CALCULATION["base_rate"]
    multiplier = MOCK_COST_CALCULATION["duration_multipliers"].get(duration, 1.0)
    return energy_amount * base_rate * multiplier