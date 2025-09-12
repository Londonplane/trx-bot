#!/usr/bin/env python3
"""
TRON Shasta测试网钱包生成工具
生成3个随机TRON钱包地址，用于测试
"""

import json
import os
from datetime import datetime
from tronpy import Tron
from tronpy.keys import PrivateKey


class WalletGenerator:
    """TRON钱包生成器"""
    
    def __init__(self):
        """初始化，连接到Shasta测试网"""
        try:
            # 连接到Shasta测试网
            self.client = Tron(network='shasta')
            print("成功连接到 TRON Shasta 测试网")
        except Exception as e:
            print(f"连接Shasta测试网失败: {e}")
            raise
    
    def generate_wallet(self) -> dict:
        """生成一个随机TRON钱包"""
        try:
            # 生成随机私钥
            private_key = PrivateKey.random()
            
            # 获取钱包地址
            address = private_key.public_key.to_base58check_address()
            
            # 返回钱包信息
            wallet_info = {
                'address': address,
                'private_key': private_key.hex(),
                'public_key': private_key.public_key.hex(),
                'created_at': datetime.now().isoformat(),
                'network': 'Shasta Testnet'
            }
            
            print(f"生成钱包: {address}")
            return wallet_info
            
        except Exception as e:
            print(f"生成钱包失败: {e}")
            raise
    
    def generate_multiple_wallets(self, count: int = 3) -> list:
        """生成多个钱包"""
        wallets = []
        
        print(f"开始生成 {count} 个TRON钱包...")
        
        for i in range(count):
            print(f"\n生成第 {i+1} 个钱包:")
            wallet = self.generate_wallet()
            wallets.append(wallet)
        
        print(f"\n成功生成 {len(wallets)} 个钱包!")
        return wallets
    
    def save_wallets_to_file(self, wallets: list, filename: str = 'wallets.json') -> str:
        """保存钱包信息到JSON文件"""
        try:
            # 获取当前脚本目录
            script_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_dir, filename)
            
            # 准备保存的数据
            data = {
                'generated_at': datetime.now().isoformat(),
                'network': 'Shasta Testnet',
                'total_wallets': len(wallets),
                'wallets': wallets,
                'notes': [
                    '这些是Shasta测试网钱包，仅用于测试',
                    '私钥信息敏感，请妥善保管',
                    '可通过 @TronTest2 推特获取免费测试TRX',
                    '测试网地址: https://shasta.tronex.io/'
                ]
            }
            
            # 保存到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"钱包信息已保存到: {file_path}")
            return file_path
            
        except Exception as e:
            print(f"保存钱包文件失败: {e}")
            raise
    
    def display_wallets_summary(self, wallets: list):
        """显示钱包摘要信息"""
        print("\n" + "="*80)
        print("TRON SHASTA 测试网钱包生成报告")
        print("="*80)
        
        for i, wallet in enumerate(wallets, 1):
            print(f"\n钱包 #{i}:")
            print(f"   地址: {wallet['address']}")
            print(f"   私钥: {wallet['private_key'][:20]}...{wallet['private_key'][-20:]}")
            print(f"   创建时间: {wallet['created_at']}")
        
        print(f"\n总计: {len(wallets)} 个钱包")
        print("网络: TRON Shasta 测试网")
        print("浏览器: https://shasta.tronex.io/")
        
        print("\n获取免费测试TRX:")
        print("   1. 关注 Twitter @TronTest2")
        print("   2. 发推文提及 @TronTest2 和你的钱包地址")
        print("   3. 等待5分钟即可收到10,000测试TRX")
        
        print("\n安全提醒:")
        print("   - 这些是测试网钱包，仅用于开发测试")
        print("   - 私钥信息已保存到wallets.json，请妥善保管")
        print("   - 不要在主网使用相同的私钥")


def main():
    """主函数"""
    print("TRON Shasta测试网钱包生成器")
    print("="*50)
    
    try:
        # 创建钱包生成器
        generator = WalletGenerator()
        
        # 生成3个钱包
        wallets = generator.generate_multiple_wallets(3)
        
        # 保存到文件
        file_path = generator.save_wallets_to_file(wallets)
        
        # 显示摘要
        generator.display_wallets_summary(wallets)
        
        print(f"\n生成完成! 钱包信息已保存到: {file_path}")
        
    except Exception as e:
        print(f"\n操作失败: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())