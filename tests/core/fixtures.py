"""
测试数据装置(Fixtures)

提供预定义的测试数据和场景，用于各种测试用例。
"""

from typing import Dict, List, Any
from .test_wallets import wallet_manager

# 闪租页面测试装置
FLASH_RENTAL_FIXTURES = {
    "energy_selections": [
        {"amount": 65000, "display": "65 000", "button_text": "🔸 65K"},
        {"amount": 135000, "display": "135 000", "button_text": "🔸 135K"},
        {"amount": 270000, "display": "270 000", "button_text": "🔸 270K"},
        {"amount": 540000, "display": "540 000", "button_text": "🔸 540K"},
        {"amount": 1000000, "display": "1 000 000", "button_text": "🔸 1M"}
    ],
    
    "duration_selections": [
        {"value": "1h", "display": "1h", "button_text": "🔸 1h"},
        {"value": "1d", "display": "1d", "button_text": "🔸 1d"},
        {"value": "3d", "display": "3d", "button_text": "🔸 3d"},
        {"value": "7d", "display": "7d", "button_text": "🔸 7d"},
        {"value": "14d", "display": "14d", "button_text": "🔸 14d"}
    ],
    
    "custom_energy_inputs": [
        {"input": "50000", "expected": 50000},
        {"input": "100K", "expected": 100000},
        {"input": "1M", "expected": 1000000},
        {"input": "1.5M", "expected": 1500000}
    ]
}

# 余额查询测试装置
BALANCE_QUERY_FIXTURES = {
    "expected_balances": {
        "customer": {
            "trx_balance": 1000.0,
            "energy_available": 0,
            "bandwidth_available": 395,
            "tolerance": 1.0
        },
        "platform": {
            "trx_balance": 7000.0, 
            "energy_available": 0,
            "bandwidth_available": 395,
            "tolerance": 1.0
        },
        "supplier": {
            "trx_balance": 2000.0,
            "energy_available": 0,
            "bandwidth_available": 395,
            "tolerance": 1.0
        }
    },
    
    "mock_responses": {
        "success": {
            "trx_balance": 1000.0,
            "energy_available": 0,
            "bandwidth_available": 395
        },
        "empty_account": {
            "trx_balance": 0.0,
            "energy_available": 0,
            "bandwidth_available": 0
        },
        "error": None
    }
}

# 订单测试装置
ORDER_TEST_FIXTURES = {
    "valid_orders": [
        {
            "energy_amount": 135000,
            "duration": "1d",
            "customer_address": wallet_manager.get_customer_wallet().address,
            "expected_cost": 4.86
        },
        {
            "energy_amount": 65000,
            "duration": "1h", 
            "customer_address": wallet_manager.get_customer_wallet().address,
            "expected_cost": 2.925
        },
        {
            "energy_amount": 1000000,
            "duration": "7d",
            "customer_address": wallet_manager.get_customer_wallet().address,
            "expected_cost": 27.0
        }
    ],
    
    "invalid_orders": [
        {
            "energy_amount": 0,
            "duration": "1d",
            "error": "能量数量必须大于0"
        },
        {
            "energy_amount": 135000,
            "duration": "invalid",
            "error": "无效的租期"
        }
    ]
}

# 三方交易流程测试装置
BUSINESS_FLOW_FIXTURES = {
    "transaction_scenarios": [
        {
            "name": "标准135K能量1天订单",
            "description": "最常见的能量租赁订单场景",
            "customer_wallet": "customer",
            "platform_wallet": "platform", 
            "supplier_wallet": "supplier",
            "energy_amount": 135000,
            "duration": "1d",
            "expected_cost": 4.86,
            "steps": [
                "顾客选择135K能量，租期1天",
                "系统计算费用约4.86 TRX",
                "顾客确认订单，获得平台支付地址",
                "顾客向平台转账4.86 TRX",
                "平台确认收款，创建供应订单",
                "供应商向顾客地址转移135K能量",
                "系统确认交易完成"
            ]
        },
        {
            "name": "大额1M能量7天订单",
            "description": "大额长期能量租赁场景",
            "customer_wallet": "customer",
            "platform_wallet": "platform",
            "supplier_wallet": "supplier", 
            "energy_amount": 1000000,
            "duration": "7d",
            "expected_cost": 27.0,
            "steps": [
                "顾客选择1M能量，租期7天",
                "系统计算费用约27.0 TRX",
                "验证顾客余额充足(1000 TRX)",
                "执行交易流程",
                "验证大额能量转移"
            ]
        }
    ],
    
    "edge_cases": [
        {
            "name": "余额不足场景",
            "description": "顾客余额不足支付订单",
            "issue": "顾客余额 < 订单费用",
            "expected_behavior": "显示余额不足错误，阻止订单创建"
        },
        {
            "name": "网络异常场景", 
            "description": "区块链网络异常或API不可用",
            "issue": "TRON网络连接失败",
            "expected_behavior": "显示网络错误，提供重试选项"
        }
    ]
}

# UI交互测试装置
UI_TEST_FIXTURES = {
    "button_interactions": [
        {"button_text": "Select address", "expected_action": "显示钱包管理界面"},
        {"button_text": "Address balance", "expected_action": "查询并更新余额信息"},
        {"button_text": "Buy", "expected_action": "创建能量租赁订单"},
        {"button_text": "Change address", "expected_action": "返回地址选择界面"}
    ],
    
    "message_formats": [
        {
            "scenario": "选择参数后显示",
            "expected_format": [
                "Calculation of the cost of purchasing energy:",
                "🎯 Address:",
                "ℹ️ Address balance:",
                "⚡️ Amount:",
                "📆 Period:",
                "💵 Cost:"
            ]
        },
        {
            "scenario": "余额更新中显示", 
            "expected_format": "🔄 Updating balance…"
        }
    ]
}

def get_test_fixture(category: str, name: str = None) -> Any:
    """获取测试装置数据"""
    fixtures = {
        "flash_rental": FLASH_RENTAL_FIXTURES,
        "balance_query": BALANCE_QUERY_FIXTURES,
        "order_test": ORDER_TEST_FIXTURES,
        "business_flow": BUSINESS_FLOW_FIXTURES,
        "ui_test": UI_TEST_FIXTURES
    }
    
    fixture = fixtures.get(category)
    if name and isinstance(fixture, dict):
        return fixture.get(name)
    return fixture

def get_wallet_fixture(wallet_type: str) -> Dict:
    """获取指定钱包的测试装置"""
    return BALANCE_QUERY_FIXTURES["expected_balances"].get(wallet_type)