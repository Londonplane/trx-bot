#!/usr/bin/env python3
"""
设置测试环境的供应商钱包
为测试钱包C生成私钥并添加到后端供应商钱包池
"""
import requests
import json
from tronpy import Tron
from tronpy.keys import PrivateKey

def generate_test_wallet():
    """生成测试钱包私钥和地址"""
    # 生成随机私钥
    private_key = PrivateKey.random()
    address = private_key.public_key.to_base58check_address()
    
    return {
        'private_key': private_key.hex(),
        'address': address
    }

def add_supplier_wallet_to_backend(private_key):
    """将供应商钱包添加到后端"""
    url = "http://localhost:8002/api/supplier-wallets/add"
    payload = {
        "private_key": private_key
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"添加供应商钱包失败: {e}")
        return None

def main():
    print("设置测试环境供应商钱包...")
    
    # 方案1: 为现有测试钱包C生成私钥
    test_wallet_c_address = "TVAcKMkSvL8Jbf58AKLnWFesYjiznUnr4"
    
    print(f"测试钱包C地址: {test_wallet_c_address}")
    print("注意: 由于我们没有真实的钱包C私钥，将生成一个新的测试钱包作为供应商")
    
    # 生成新的测试供应商钱包
    supplier_wallet = generate_test_wallet()
    
    print(f"\n生成的测试供应商钱包:")
    print(f"地址: {supplier_wallet['address']}")
    print(f"私钥: {supplier_wallet['private_key'][:10]}...{supplier_wallet['private_key'][-10:]}")
    
    # 添加到后端
    print(f"\n添加到后端供应商钱包池...")
    result = add_supplier_wallet_to_backend(supplier_wallet['private_key'])
    
    if result:
        print(f"供应商钱包添加成功!")
        print(f"ID: {result['id']}")
        print(f"地址: {result['wallet_address']}")
        print(f"TRX余额: {result['trx_balance']}")
        print(f"能量: {result['energy_available']}")
        print(f"状态: {'活跃' if result['is_active'] else '非活跃'}")
    else:
        print("供应商钱包添加失败!")
        return False
    
    # 保存钱包信息到文件
    wallet_info = {
        "test_supplier_wallet": {
            "address": supplier_wallet['address'],
            "private_key": supplier_wallet['private_key'],
            "role": "供应商 - 提供能量给顾客",
            "network": "Shasta测试网",
            "created_for_testing": True
        }
    }
    
    with open('test_supplier_wallet.json', 'w', encoding='utf-8') as f:
        json.dump(wallet_info, f, indent=2, ensure_ascii=False)
    
    print(f"\n钱包信息已保存到: test_supplier_wallet.json")
    print(f"\n重要提示:")
    print(f"1. 这是Shasta测试网钱包，不能用于主网交易")
    print(f"2. 需要为该钱包充值TRX和Energy才能执行交易")  
    print(f"3. 可以通过Shasta测试网水龙头获取测试TRX:")
    print(f"   https://www.trongrid.io/shasta/")
    
    return True

if __name__ == "__main__":
    main()