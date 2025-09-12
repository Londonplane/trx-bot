#!/usr/bin/env python3
"""
测试能量查询差异 - 对比TronPy和TronScan API的结果
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tronpy import Tron
from tron_api import TronAPI

def test_wallet3_energy():
    """测试钱包3的能量查询"""
    # 钱包3地址
    address = "TVAcKMkSvL8Jbf58AKLnWFesYjiznNUnr4"
    
    print(f"测试地址: {address}")
    print("=" * 60)
    
    # 方法1: 使用TronPy (stake_manager.py使用的方法)
    print("\n方法1: TronPy 直接查询")
    print("-" * 30)
    try:
        client = Tron(network='shasta')
        resources = client.get_account_resource(address)
        energy_limit = resources.get('EnergyLimit', 0)
        energy_used = resources.get('EnergyUsed', 0)
        energy_available = max(0, energy_limit - energy_used)
        
        print(f"EnergyLimit: {energy_limit:,}")
        print(f"EnergyUsed: {energy_used:,}")
        print(f"Energy可用: {energy_available:,}")
        print(f"原始数据: {resources}")
        
    except Exception as e:
        print(f"TronPy查询失败: {e}")
    
    # 方法2: 使用TronScan API (wallet_checker.py使用的方法)
    print("\n方法2: TronScan API")
    print("-" * 30)
    try:
        tron_api = TronAPI(network="shasta")
        balance = tron_api.get_account_balance(address)
        
        if balance:
            print(f"Energy可用: {balance.energy_available:,}")
            print(f"EnergyLimit: {balance.energy_limit:,}")
            print(f"EnergyUsed: {balance.energy_used:,}")
        else:
            print("TronScan API查询失败")
            
    except Exception as e:
        print(f"TronScan API异常: {e}")
    
    # 方法3: 直接使用TronScan URL测试
    print("\n方法3: 直接TronScan URL测试")
    print("-" * 30)
    try:
        import requests
        url = f"https://shastapi.tronscan.org/api/account?address={address}&includeToken=false"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        energy_data = data.get('energy', {})
        print(f"TronScan原始energy数据: {energy_data}")
        
        energy_limit = energy_data.get('energyLimit', 0)
        energy_used = energy_data.get('energyUsed', 0)
        print(f"从TronScan解析: Limit={energy_limit:,}, Used={energy_used:,}")
        
    except Exception as e:
        print(f"直接URL测试失败: {e}")

if __name__ == "__main__":
    test_wallet3_energy()