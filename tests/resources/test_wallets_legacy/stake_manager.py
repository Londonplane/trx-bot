#!/usr/bin/env python3
"""
TRON Shasta测试网质押管理工具
支持质押TRX获得Energy/Bandwidth和解除质押操作
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tronpy import Tron
from tronpy.keys import PrivateKey
from tronpy.exceptions import TransactionError

class StakeManager:
    """质押管理器"""
    
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.wallets_file = os.path.join(self.script_dir, 'wallets.json')
        self.client = Tron(network='shasta')
        print("连接到 TRON Shasta 测试网")
        
    def load_wallets(self) -> List[Dict[str, Any]]:
        """加载钱包信息"""
        try:
            if not os.path.exists(self.wallets_file):
                print(f"钱包文件不存在: {self.wallets_file}")
                return []
            
            with open(self.wallets_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data.get('wallets', [])
            
        except Exception as e:
            print(f"加载钱包文件失败: {e}")
            return []
    
    def display_wallets(self, wallets: List[Dict[str, Any]]):
        """显示钱包列表"""
        print("\n可用钱包:")
        print("="*70)
        
        for i, wallet in enumerate(wallets, 1):
            address = wallet['address']
            
            # 查询当前余额
            try:
                account = self.client.get_account(address)
                balance = account.get('balance', 0) / 1_000_000  # SUN转TRX
                
                # 查询资源信息
                resources = self.client.get_account_resource(address)
                energy_limit = resources.get('EnergyLimit', 0)
                bandwidth_limit = resources.get('NetLimit', 0)
                
                print(f"{i}. {address}")
                print(f"   TRX余额: {balance:.6f}")
                print(f"   Energy: {energy_limit:,}")
                print(f"   Bandwidth: {bandwidth_limit:,}")
                print()
                
            except Exception as e:
                print(f"{i}. {address}")
                print(f"   查询余额失败: {e}")
                print()
    
    def select_wallet(self, wallets: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """选择钱包"""
        while True:
            try:
                choice = input(f"请选择钱包 (1-{len(wallets)}) 或输入 'q' 退出: ").strip()
                
                if choice.lower() == 'q':
                    return None
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(wallets):
                    return wallets[choice_num - 1]
                else:
                    print(f"请输入 1-{len(wallets)} 之间的数字")
                    
            except ValueError:
                print("请输入有效的数字")
    
    def get_stake_amount(self, max_balance: float) -> Optional[float]:
        """获取质押数量"""
        while True:
            try:
                amount_str = input(f"请输入质押数量 (TRX, 最大: {max_balance:.6f}) 或输入 'back' 返回: ").strip()
                
                if amount_str.lower() == 'back':
                    return None
                
                amount = float(amount_str)
                
                if amount <= 0:
                    print("质押数量必须大于0")
                    continue
                
                if amount > max_balance:
                    print(f"质押数量不能超过余额 {max_balance:.6f} TRX")
                    continue
                
                # TRON质押最小单位检查 (通常最小1 TRX)
                if amount < 1:
                    print("最小质押数量为 1 TRX")
                    continue
                
                return amount
                
            except ValueError:
                print("请输入有效的数字")
    
    def stake_for_energy(self, wallet: Dict[str, Any], amount: float) -> bool:
        """质押TRX获得Energy"""
        try:
            private_key = PrivateKey(bytes.fromhex(wallet['private_key']))
            address = wallet['address']
            
            print(f"\n开始质押操作...")
            print(f"地址: {address}")
            print(f"数量: {amount} TRX")
            print(f"类型: 获得Energy")
            
            # 转换为SUN单位
            amount_sun = int(amount * 1_000_000)
            
            # 构建质押交易 (修复API参数)
            txn = (
                self.client.trx.freeze_balance(
                    owner=address,
                    amount=amount_sun,
                    resource='ENERGY'
                )
                .fee_limit(1_000_000)  # 设置手续费限制
                .build()
                .sign(private_key)
            )
            
            # 广播交易
            result = txn.broadcast()
            
            if result.get('result'):
                print(f"质押成功!")
                print(f"交易ID: {result.get('txid')}")
                print(f"等待确认...")
                
                # 等待交易确认
                import time
                time.sleep(5)  # 增加等待时间
                
                return True
            else:
                error_msg = result.get('message', '未知错误')
                print(f"质押失败: {error_msg}")
                return False
                
        except TransactionError as e:
            print(f"交易错误: {e}")
            return False
        except Exception as e:
            print(f"质押失败: {e}")
            return False
    
    def stake_for_bandwidth(self, wallet: Dict[str, Any], amount: float) -> bool:
        """质押TRX获得Bandwidth"""
        try:
            private_key = PrivateKey(bytes.fromhex(wallet['private_key']))
            address = wallet['address']
            
            print(f"\n开始质押操作...")
            print(f"地址: {address}")
            print(f"数量: {amount} TRX")
            print(f"类型: 获得Bandwidth")
            
            # 转换为SUN单位
            amount_sun = int(amount * 1_000_000)
            
            # 构建质押交易 (修复API参数)
            txn = (
                self.client.trx.freeze_balance(
                    owner=address,
                    amount=amount_sun,
                    resource='BANDWIDTH'
                )
                .fee_limit(1_000_000)  # 设置手续费限制
                .build()
                .sign(private_key)
            )
            
            # 广播交易
            result = txn.broadcast()
            
            if result.get('result'):
                print(f"质押成功!")
                print(f"交易ID: {result.get('txid')}")
                print(f"等待确认...")
                
                # 等待交易确认
                import time
                time.sleep(5)  # 增加等待时间
                
                return True
            else:
                error_msg = result.get('message', '未知错误')
                print(f"质押失败: {error_msg}")
                return False
                
        except TransactionError as e:
            print(f"交易错误: {e}")
            return False
        except Exception as e:
            print(f"质押失败: {e}")
            return False
    
    def unfreeze_balance(self, wallet: Dict[str, Any], resource_type: str) -> bool:
        """解除质押"""
        try:
            private_key = PrivateKey(bytes.fromhex(wallet['private_key']))
            address = wallet['address']
            
            print(f"\n开始解除质押操作...")
            print(f"地址: {address}")
            print(f"类型: {resource_type}")
            
            # 构建解除质押交易 (修复API参数)
            txn = (
                self.client.trx.unfreeze_balance(
                    owner=address,
                    resource=resource_type
                )
                .fee_limit(1_000_000)  # 设置手续费限制
                .build()
                .sign(private_key)
            )
            
            # 广播交易
            result = txn.broadcast()
            
            if result.get('result'):
                print(f"解除质押成功!")
                print(f"交易ID: {result.get('txid')}")
                print(f"等待确认...")
                
                # 等待交易确认
                import time
                time.sleep(5)  # 增加等待时间
                
                return True
            else:
                error_msg = result.get('message', '未知错误')
                print(f"解除质押失败: {error_msg}")
                return False
                
        except TransactionError as e:
            print(f"交易错误: {e}")
            return False
        except Exception as e:
            print(f"解除质押失败: {e}")
            return False
    
    def show_account_info(self, address: str):
        """显示账户详细信息"""
        try:
            print(f"\n账户详细信息:")
            print("="*60)
            
            # 基本账户信息
            account = self.client.get_account(address)
            balance = account.get('balance', 0) / 1_000_000
            
            print(f"地址: {address}")
            print(f"TRX余额: {balance:.6f}")
            
            # 资源信息
            resources = self.client.get_account_resource(address)
            
            # Energy信息
            energy_limit = resources.get('EnergyLimit', 0)
            energy_used = resources.get('EnergyUsed', 0)
            energy_available = max(0, energy_limit - energy_used)
            
            print(f"\nEnergy资源:")
            print(f"  总限制: {energy_limit:,}")
            print(f"  已使用: {energy_used:,}")
            print(f"  可用: {energy_available:,}")
            
            # Bandwidth信息
            net_limit = resources.get('NetLimit', 0)
            net_used = resources.get('NetUsed', 0)
            net_available = max(0, net_limit - net_used)
            
            free_net_limit = resources.get('freeNetLimit', 1500)
            free_net_used = resources.get('freeNetUsed', 0)
            free_net_available = max(0, free_net_limit - free_net_used)
            
            total_bandwidth = net_limit + free_net_limit
            total_used = net_used + free_net_used
            total_available = net_available + free_net_available
            
            print(f"\nBandwidth资源:")
            print(f"  质押带宽: {net_available:,}/{net_limit:,}")
            print(f"  免费带宽: {free_net_available:,}/{free_net_limit:,}")
            print(f"  总可用: {total_available:,}")
            
            # 质押信息
            frozen_v2 = account.get('frozen_v2', [])
            if frozen_v2:
                print(f"\n质押信息:")
                for frozen in frozen_v2:
                    resource_type = frozen.get('type', 'UNKNOWN')
                    amount = frozen.get('amount', 0) / 1_000_000
                    print(f"  {resource_type}: {amount:.6f} TRX")
            else:
                print(f"\n质押信息: 无质押")
            
            print("="*60)
            
        except Exception as e:
            print(f"查询账户信息失败: {e}")
    
    def interactive_menu(self):
        """交互式菜单"""
        wallets = self.load_wallets()
        if not wallets:
            print("没有找到钱包文件，请先运行 wallet_generator.py")
            return
        
        while True:
            print("\n" + "="*60)
            print("TRON Shasta 质押管理工具")
            print("="*60)
            
            self.display_wallets(wallets)
            
            print("操作选项:")
            print("1. 质押TRX获得Energy")
            print("2. 质押TRX获得Bandwidth") 
            print("3. 解除Energy质押")
            print("4. 解除Bandwidth质押")
            print("5. 查看账户详细信息")
            print("6. 刷新钱包状态")
            print("q. 退出")
            
            choice = input("\n请选择操作 (1-6, q): ").strip()
            
            if choice == 'q':
                print("退出程序")
                break
            elif choice == '1':
                self.handle_stake_energy(wallets)
            elif choice == '2':
                self.handle_stake_bandwidth(wallets)
            elif choice == '3':
                self.handle_unfreeze_energy(wallets)
            elif choice == '4':
                self.handle_unfreeze_bandwidth(wallets)
            elif choice == '5':
                self.handle_show_account_info(wallets)
            elif choice == '6':
                print("刷新钱包状态...")
                continue
            else:
                print("无效选择，请重试")
    
    def handle_stake_energy(self, wallets: List[Dict[str, Any]]):
        """处理质押Energy操作"""
        wallet = self.select_wallet(wallets)
        if not wallet:
            return
        
        # 获取当前余额
        try:
            account = self.client.get_account(wallet['address'])
            balance = account.get('balance', 0) / 1_000_000
            
            if balance < 1:
                print(f"余额不足，当前余额: {balance:.6f} TRX")
                return
            
            amount = self.get_stake_amount(balance)
            if amount is None:
                return
            
            # 确认操作
            print(f"\n确认质押操作:")
            print(f"钱包: {wallet['address']}")
            print(f"数量: {amount} TRX")
            print(f"获得: Energy资源")
            print(f"锁定期: 3天")
            
            confirm = input("确认执行? (y/N): ").strip().lower()
            if confirm == 'y':
                success = self.stake_for_energy(wallet, amount)
                if success:
                    print("质押完成，3秒后显示更新后的账户信息...")
                    import time
                    time.sleep(3)
                    self.show_account_info(wallet['address'])
            
        except Exception as e:
            print(f"操作失败: {e}")
    
    def handle_stake_bandwidth(self, wallets: List[Dict[str, Any]]):
        """处理质押Bandwidth操作"""
        wallet = self.select_wallet(wallets)
        if not wallet:
            return
        
        # 获取当前余额
        try:
            account = self.client.get_account(wallet['address'])
            balance = account.get('balance', 0) / 1_000_000
            
            if balance < 1:
                print(f"余额不足，当前余额: {balance:.6f} TRX")
                return
            
            amount = self.get_stake_amount(balance)
            if amount is None:
                return
            
            # 确认操作
            print(f"\n确认质押操作:")
            print(f"钱包: {wallet['address']}")
            print(f"数量: {amount} TRX")
            print(f"获得: Bandwidth资源")
            print(f"锁定期: 3天")
            
            confirm = input("确认执行? (y/N): ").strip().lower()
            if confirm == 'y':
                success = self.stake_for_bandwidth(wallet, amount)
                if success:
                    print("质押完成，3秒后显示更新后的账户信息...")
                    import time
                    time.sleep(3)
                    self.show_account_info(wallet['address'])
            
        except Exception as e:
            print(f"操作失败: {e}")
    
    def handle_unfreeze_energy(self, wallets: List[Dict[str, Any]]):
        """处理解除Energy质押"""
        wallet = self.select_wallet(wallets)
        if not wallet:
            return
        
        print(f"\n确认解除质押:")
        print(f"钱包: {wallet['address']}")
        print(f"类型: Energy资源")
        print("注意: 解除质押后需要等待确认")
        
        confirm = input("确认执行? (y/N): ").strip().lower()
        if confirm == 'y':
            success = self.unfreeze_balance(wallet, 'ENERGY')
            if success:
                print("解除质押完成，3秒后显示更新后的账户信息...")
                import time
                time.sleep(3)
                self.show_account_info(wallet['address'])
    
    def handle_unfreeze_bandwidth(self, wallets: List[Dict[str, Any]]):
        """处理解除Bandwidth质押"""
        wallet = self.select_wallet(wallets)
        if not wallet:
            return
        
        print(f"\n确认解除质押:")
        print(f"钱包: {wallet['address']}")
        print(f"类型: Bandwidth资源")
        print("注意: 解除质押后需要等待确认")
        
        confirm = input("确认执行? (y/N): ").strip().lower()
        if confirm == 'y':
            success = self.unfreeze_balance(wallet, 'BANDWIDTH')
            if success:
                print("解除质押完成，3秒后显示更新后的账户信息...")
                import time
                time.sleep(3)
                self.show_account_info(wallet['address'])
    
    def handle_show_account_info(self, wallets: List[Dict[str, Any]]):
        """显示账户详细信息"""
        wallet = self.select_wallet(wallets)
        if wallet:
            self.show_account_info(wallet['address'])

def main():
    """主函数"""
    try:
        manager = StakeManager()
        manager.interactive_menu()
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序出错: {e}")

if __name__ == "__main__":
    main()