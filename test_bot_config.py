#!/usr/bin/env python3
"""
直接测试Bot使用的TronAPI配置
"""

import os
import sys
import logging

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tron_api import TronAPI
from config import TRON_NETWORK

def test_bot_config():
    """测试Bot使用的配置"""
    print(f"测试Bot配置 - 网络: {TRON_NETWORK}")
    
    # 钱包3地址（有14,088能量的地址）
    address = "TVAcKMkSvL8Jbf58AKLnWFesYjiznNUnr4"
    
    try:
        # 创建API客户端（与Bot相同的配置）
        api = TronAPI(
            network=TRON_NETWORK,
            api_key=os.getenv('TRON_API_KEY')
        )
        
        print(f"API配置: network={api.network}, api_url={api.api_url}")
        print(f"正在查询地址: {address}")
        
        # 查询余额
        balance = api.get_account_balance(address)
        
        if balance:
            print(f"✅ 查询成功!")
            print(f"TRX: {balance.trx_balance:.6f}")
            print(f"Energy可用: {balance.energy_available:,}")
            print(f"EnergyLimit: {balance.energy_limit:,}")
            print(f"Bandwidth可用: {balance.bandwidth_available:,}")
            
            # 这是Bot会设置的会话数据
            address_balance = {
                'TRX': f"{balance.trx_balance:.6f}",
                'ENERGY': f"{balance.energy_available:,}",
                'BANDWIDTH': f"{balance.bandwidth_available:,}"
            }
            print(f"\nBot会话数据:")
            print(f"TRX: {address_balance['TRX']}")
            print(f"ENERGY: {address_balance['ENERGY']}")  # 这个应该显示14,088
            print(f"BANDWIDTH: {address_balance['BANDWIDTH']}")
            
        else:
            print(f"❌ 查询失败")
            
    except Exception as e:
        print(f"❌ 异常: {e}")

if __name__ == "__main__":
    # 启用日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    test_bot_config()