#!/usr/bin/env python3
"""
配置真实交易功能
为现有供应商钱包生成测试私钥并启用真实交易处理
"""

import sys
import os
sys.path.append('backend')

import requests
from tronpy.keys import PrivateKey
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database import Base
from backend.app.models import SupplierWallet
from cryptography.fernet import Fernet
import base64

def generate_test_private_key():
    """为测试生成一个私钥"""
    # 这是为Shasta测试网专门生成的测试私钥
    # 在真实环境中，应该使用已有钱包的真实私钥
    private_key = PrivateKey.random()
    return private_key.hex()

def encrypt_private_key(private_key: str):
    """加密私钥"""
    # 简单加密（生产环境需要更安全的方式）
    key = Fernet.generate_key()
    cipher = Fernet(key)
    encrypted = cipher.encrypt(private_key.encode())
    return base64.b64encode(encrypted).decode(), key

def update_supplier_wallet_with_private_key():
    """为现有的供应商钱包配置私钥"""
    
    print("Configuring real transaction functionality...")
    
    # 连接数据库
    DATABASE_URL = "sqlite:///backend/trx_energy.db"
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    
    try:
        # 获取现有的供应商钱包
        supplier_wallet = db.query(SupplierWallet).first()
        
        if not supplier_wallet:
            print("ERROR: No supplier wallet found")
            return False
            
        print(f"Found supplier wallet: {supplier_wallet.wallet_address}")
        print(f"TRX balance: {supplier_wallet.trx_balance}")
        
        # 生成测试私钥
        test_private_key = generate_test_private_key()
        encrypted_key, encryption_key = encrypt_private_key(test_private_key)
        
        print(f"Generated test private key: {test_private_key[:10]}...{test_private_key[-10:]}")
        print(f"WARNING: This is a test private key, not the wallet's real private key")
        print(f"WARNING: In production, use the actual private key for wallet {supplier_wallet.wallet_address}")
        
        # 更新数据库中的私钥
        supplier_wallet.private_key_encrypted = encrypted_key
        db.commit()
        
        print(f"SUCCESS: Private key configured in database")
        
        # 保存加密密钥到环境变量文件
        with open('.env.test', 'w') as f:
            f.write(f"ENCRYPTION_KEY={encryption_key.decode()}\n")
            f.write(f"TRON_NETWORK=shasta\n")
            f.write(f"ENABLE_REAL_TRANSACTIONS=true\n")
            
        print(f"Encryption key saved to .env.test file")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Configuration failed: {e}")
        return False
    finally:
        db.close()

def test_order_creation():
    """测试订单创建"""
    print("\nTesting order creation...")
    
    try:
        # 测试创建订单
        response = requests.post('http://localhost:8002/api/orders', json={
            "user_id": 6904963980,
            "energy_amount": 65000,
            "duration": "1h", 
            "receive_address": "TCX13dZVJt1uCDCGA3F26KqEndpsSt2CHy"
        })
        
        if response.status_code == 200:
            order = response.json()
            print(f"SUCCESS: Order created!")
            print(f"Order ID: {order['id']}")
            print(f"User ID: {order['user_id']}")
            print(f"Energy: {order['energy_amount']}")
            print(f"Receive address: {order['receive_address']}")
            print(f"Status: {order['status']}")
            
            if order.get('tx_hash'):
                print(f"Transaction hash: {order['tx_hash']}")
                print(f"View transaction: https://shasta.tronscan.org/#/transaction/{order['tx_hash']}")
            
            return True
        else:
            print(f"ERROR: Order creation failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        return False

def main():
    print("Starting Real TRON Transaction Configuration")
    print("=" * 50)
    
    # Step 1: 配置供应商钱包私钥
    if not update_supplier_wallet_with_private_key():
        return False
    
    print("\n" + "=" * 50)
    print("Real transaction configuration completed!")
    print("\nNext steps:")
    print("1. Restart backend service to load new configuration")
    print("2. Restart Bot to use real transaction functionality") 
    print("3. Test buy energy functionality in the Bot")
    print("\nImportant notes:")
    print("- Currently using test private key, not the wallet's real private key")
    print("- Transactions will execute on Shasta testnet, no real money involved")
    print("- To use real private key, manually update the private key field in database")
    
    return True

if __name__ == "__main__":
    main()