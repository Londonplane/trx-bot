"""
测试钱包管理模块

统一管理所有测试钱包地址和相关信息，
提供一致的钱包访问接口。
"""

from typing import Dict, List, Optional
import json
import os

class TestWallet:
    """测试钱包数据类"""
    
    def __init__(self, address: str, private_key: str, role: str, 
                 expected_balance: float = 0.0, network: str = "shasta"):
        self.address = address
        self.private_key = private_key
        self.role = role
        self.expected_balance = expected_balance
        self.network = network
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "address": self.address,
            "private_key": self.private_key,
            "role": self.role,
            "expected_balance": self.expected_balance,
            "network": self.network
        }
    
    def __repr__(self) -> str:
        return f"TestWallet(address={self.address[:10]}..., role={self.role})"

class TestWalletManager:
    """测试钱包管理器"""
    
    def __init__(self):
        self.wallets: Dict[str, TestWallet] = {}
        self._load_wallets()
    
    def _load_wallets(self):
        """加载测试钱包数据"""
        # 三方交易模型的测试钱包
        self.wallets = {
            'customer': TestWallet(
                address='TCX13dZVJt1uCDCGA3F26KqEndpsSt2CHy',
                private_key='9268f1a74aacd9af82fb29c3761b45fd17b8e8003612646554274302b86d3168',
                role='顾客钱包 - 支付TRX购买能量服务',
                expected_balance=1000.0,
                network='shasta'
            ),
            'platform': TestWallet(
                address='TAcrAuU78UyPZpZuVPCQo2ZVcfwmkskWLz',
                private_key='0092da9cc83aff0814632e341186399b30b67617c35668b6501e59b9bb146417',
                role='平台钱包 - 接收顾客支付，处理订单管理',
                expected_balance=7000.0,
                network='shasta'
            ),
            'supplier': TestWallet(
                address='TVAcKMkSvL8Jbf58AKLnWFesYjiznNUnr4',
                private_key='c87e954fe8dd2c55d75bfb6e5db1add7cb55a0931376e085a9e78a061f7983a1',
                role='供应商钱包 - 向顾客提供能量服务',
                expected_balance=2000.0,
                network='shasta'
            )
        }
    
    def get_wallet(self, wallet_type: str) -> Optional[TestWallet]:
        """获取指定类型的测试钱包"""
        return self.wallets.get(wallet_type)
    
    def get_customer_wallet(self) -> TestWallet:
        """获取顾客钱包"""
        return self.wallets['customer']
    
    def get_platform_wallet(self) -> TestWallet:
        """获取平台钱包"""
        return self.wallets['platform']
    
    def get_supplier_wallet(self) -> TestWallet:
        """获取供应商钱包"""
        return self.wallets['supplier']
    
    def get_all_wallets(self) -> Dict[str, TestWallet]:
        """获取所有测试钱包"""
        return self.wallets
    
    def get_all_addresses(self) -> List[str]:
        """获取所有钱包地址列表"""
        return [wallet.address for wallet in self.wallets.values()]
    
    def find_wallet_by_address(self, address: str) -> Optional[TestWallet]:
        """根据地址查找钱包"""
        for wallet in self.wallets.values():
            if wallet.address == address:
                return wallet
        return None
    
    def export_wallets_json(self) -> str:
        """导出钱包数据为JSON格式"""
        wallet_data = {
            "generated_at": "2025-09-12T00:00:00.000000",
            "network": "Shasta Testnet", 
            "total_wallets": len(self.wallets),
            "business_model": "三方交易模型：顾客→平台→供应商",
            "wallets": [wallet.to_dict() for wallet in self.wallets.values()],
            "notes": [
                "这些是Shasta测试网钱包，仅用于测试",
                "私钥信息敏感，请妥善保管",
                "可通过 @TronTest2 推特获取免费测试TRX",
                "测试网地址: https://shasta.tronex.io/"
            ]
        }
        return json.dumps(wallet_data, indent=2, ensure_ascii=False)

# 全局钱包管理器实例
wallet_manager = TestWalletManager()

# 便捷访问函数
def get_customer_wallet() -> TestWallet:
    """获取顾客测试钱包"""
    return wallet_manager.get_customer_wallet()

def get_platform_wallet() -> TestWallet:
    """获取平台测试钱包"""
    return wallet_manager.get_platform_wallet()

def get_supplier_wallet() -> TestWallet:
    """获取供应商测试钱包"""
    return wallet_manager.get_supplier_wallet()

def get_test_addresses() -> List[str]:
    """获取所有测试钱包地址"""
    return wallet_manager.get_all_addresses()