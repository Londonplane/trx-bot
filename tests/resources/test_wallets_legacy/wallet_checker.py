#!/usr/bin/env python3
"""
TRON钱包余额查询工具
从wallets.json加载钱包信息，查询余额/能量/带宽
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# 添加父目录到路径，以便导入项目模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tron_api import TronAPI, AccountBalance

# USDT TRC20合约地址 (主网和测试网不同)
USDT_CONTRACT_ADDRESSES = {
    "mainnet": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
    "shasta": "TG3XXyExBkPp9nzdajDZsozEu4BkaSJozs",  # Shasta测试网USDT
    "nile": "TXYZopYRdj2D9XRtbG411XZZ3kM5VkAeBf"     # Nile测试网USDT
}

class WalletChecker:
    """钱包信息查询器"""
    
    def __init__(self, network: str = "shasta"):
        """
        初始化钱包查询器
        
        Args:
            network: 网络类型 ("mainnet", "shasta", "nile")
        """
        self.network = network
        self.tron_api = TronAPI(network=network)
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.wallets_file = os.path.join(self.script_dir, 'wallets.json')
        
        # 初始化TronPy客户端用于TRC20查询
        try:
            from tronpy import Tron
            from tronpy.providers import HTTPProvider
            
            # 使用HTTP Provider获得更好的稳定性
            if network == "mainnet":
                self.tronpy_client = Tron(network=network)
            else:
                # 测试网络使用默认配置
                self.tronpy_client = Tron(network=network)
                
            print(f"连接到 TRON {network.upper()} 网络成功")
            
        except ImportError:
            print("TronPy库未安装，将跳过TRC20代币查询")
            self.tronpy_client = None
        except Exception as e:
            print(f"TronPy初始化失败: {e}")
            self.tronpy_client = None
    
    def load_wallets(self) -> List[Dict[str, Any]]:
        """从JSON文件加载钱包信息"""
        try:
            if not os.path.exists(self.wallets_file):
                print(f"钱包文件不存在: {self.wallets_file}")
                print("请先运行 wallet_generator.py 生成钱包")
                return []
            
            with open(self.wallets_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            wallets = data.get('wallets', [])
            print(f"成功加载 {len(wallets)} 个钱包")
            return wallets
            
        except Exception as e:
            print(f"加载钱包文件失败: {e}")
            return []
    
    def get_usdt_balance(self, address: str) -> float:
        """查询USDT TRC20余额"""
        try:
            if not self.tronpy_client:
                return 0.0
            
            # 根据网络选择正确的USDT合约地址
            usdt_contract_address = USDT_CONTRACT_ADDRESSES.get(self.network)
            if not usdt_contract_address:
                print(f"不支持的网络: {self.network}")
                return 0.0
            
            # 对于测试网络，先尝试查询，如果失败再跳过
            try:
                # 获取USDT合约
                usdt_contract = self.tronpy_client.get_contract(usdt_contract_address)
                
                # 直接调用balanceOf函数，TronPy会自动处理ABI
                balance_raw = usdt_contract.functions.balanceOf(address)
                
                # USDT有6位小数，需要除以1,000,000
                usdt_balance = balance_raw / 1_000_000
                
                print(f"TronPy查询USDT成功: {usdt_balance}")
                return usdt_balance
                
            except Exception as contract_error:
                print(f"TronPy合约查询失败: {contract_error}")
                
                # 如果是测试网络且合约不存在，尝试API方法
                if self.network in ["shasta", "nile"]:
                    print("尝试API方法查询USDT...")
                    return self.get_usdt_balance_via_api(address)
                else:
                    return 0.0
            
        except Exception as e:
            print(f"USDT余额查询失败: {e}")
            return 0.0
    
    def get_usdt_balance_via_api(self, address: str) -> float:
        """通过TronScan API查询USDT余额（备用方案）"""
        try:
            import requests
            
            # 根据网络选择API端点
            if self.network == "shasta":
                api_url = "https://shastapi.tronscan.org/api/account"
            else:
                api_url = "https://apilist.tronscan.org/api/account"
            
            params = {"address": address}
            response = requests.get(api_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                trc20_balances = data.get('trc20token_balances', [])
                
                # 查找USDT余额
                usdt_contract_address = USDT_CONTRACT_ADDRESSES.get(self.network, USDT_CONTRACT_ADDRESSES["mainnet"])
                for token in trc20_balances:
                    if token.get('tokenAbbr') == 'USDT' or token.get('tokenId') == usdt_contract_address:
                        balance = float(token.get('balance', 0))
                        # USDT通常有6位小数
                        return balance / 1_000_000
                
                return 0.0
            else:
                return 0.0
                
        except Exception as e:
            print(f"API查询USDT余额失败: {e}")
            return 0.0
    
    def check_wallet_balance(self, wallet: Dict[str, Any]) -> Dict[str, Any]:
        """查询单个钱包的余额信息"""
        address = wallet['address']
        print(f"\n查询钱包: {address}")
        
        try:
            # 查询TRX余额和资源
            balance = self.tron_api.get_account_balance(address)
            
            # 查询USDT余额
            print("查询USDT余额...")
            usdt_balance = self.get_usdt_balance(address)
            
            # 如果TronPy方法失败，尝试API方法
            if usdt_balance == 0.0:
                usdt_balance = self.get_usdt_balance_via_api(address)
            
            if balance:
                result = {
                    'wallet_info': wallet,
                    'balance_info': {
                        'trx_balance': balance.trx_balance,
                        'usdt_balance': usdt_balance,  # 新增USDT余额
                        'energy_limit': balance.energy_limit,
                        'energy_used': balance.energy_used,
                        'energy_available': balance.energy_available,
                        'bandwidth_limit': balance.bandwidth_limit,
                        'bandwidth_used': balance.bandwidth_used,
                        'bandwidth_available': balance.bandwidth_available,
                        'free_net_limit': balance.free_net_limit,
                        'free_net_used': balance.free_net_used,
                    },
                    'query_time': datetime.now().isoformat(),
                    'network': self.network,
                    'status': 'success'
                }
                print(f"查询成功 - TRX: {balance.trx_balance:.6f}, USDT: {usdt_balance:.6f}")
                return result
            else:
                result = {
                    'wallet_info': wallet,
                    'balance_info': None,
                    'query_time': datetime.now().isoformat(),
                    'network': self.network,
                    'status': 'failed',
                    'error': '无法获取余额信息'
                }
                print(f"查询失败")
                return result
                
        except Exception as e:
            result = {
                'wallet_info': wallet,
                'balance_info': None,
                'query_time': datetime.now().isoformat(),
                'network': self.network,
                'status': 'error',
                'error': str(e)
            }
            print(f"查询异常: {e}")
            return result
    
    def check_all_wallets(self) -> List[Dict[str, Any]]:
        """查询所有钱包的余额信息"""
        wallets = self.load_wallets()
        if not wallets:
            return []
        
        print(f"\n开始查询 {len(wallets)} 个钱包的余额信息...")
        
        results = []
        for i, wallet in enumerate(wallets, 1):
            print(f"\n[{i}/{len(wallets)}]", end="")
            result = self.check_wallet_balance(wallet)
            results.append(result)
        
        return results
    
    def save_results(self, results: List[Dict[str, Any]], filename: str = 'balance_results.json'):
        """保存查询结果到文件"""
        try:
            file_path = os.path.join(self.script_dir, filename)
            
            data = {
                'query_time': datetime.now().isoformat(),
                'network': self.network,
                'total_wallets': len(results),
                'successful_queries': len([r for r in results if r['status'] == 'success']),
                'failed_queries': len([r for r in results if r['status'] != 'success']),
                'results': results
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"\n查询结果已保存到: {file_path}")
            return file_path
            
        except Exception as e:
            print(f"\n保存结果失败: {e}")
            return None
    
    def generate_summary_report(self, results: List[Dict[str, Any]]):
        """生成查询结果摘要报告"""
        if not results:
            print("\n没有查询结果")
            return
        
        print("\n" + "="*80)
        print(f"TRON {self.network.upper()} 钱包余额查询报告")
        print("="*80)
        
        successful_results = [r for r in results if r['status'] == 'success']
        failed_results = [r for r in results if r['status'] != 'success']
        
        print(f"\n查询统计:")
        print(f"   总钱包数: {len(results)}")
        print(f"   成功查询: {len(successful_results)}")
        print(f"   查询失败: {len(failed_results)}")
        print(f"   成功率: {len(successful_results)/len(results)*100:.1f}%")
        
        if successful_results:
            print(f"\n余额详情:")
            total_trx = 0
            total_usdt = 0  # 新增USDT总计
            total_energy = 0
            total_bandwidth = 0
            
            for i, result in enumerate(successful_results, 1):
                wallet = result['wallet_info']
                balance = result['balance_info']
                
                total_trx += balance['trx_balance']
                total_usdt += balance.get('usdt_balance', 0)  # 新增USDT计算
                total_energy += balance['energy_available']
                total_bandwidth += balance['bandwidth_available']
                
                print(f"\n   钱包 #{i}:")
                print(f"      地址: {wallet['address']}")
                print(f"      TRX余额: {balance['trx_balance']:.6f}")
                print(f"      USDT余额: {balance.get('usdt_balance', 0):.6f}")  # 新增USDT显示
                print(f"      可用能量: {balance['energy_available']:,}")
                print(f"      可用带宽: {balance['bandwidth_available']:,}")
                
                if balance['trx_balance'] == 0:
                    print(f"      余额为零，可能需要充值测试TRX")
            
            print(f"\n总计:")
            print(f"   总TRX余额: {total_trx:.6f}")
            print(f"   总USDT余额: {total_usdt:.6f}")  # 新增USDT总计显示
            print(f"   总可用能量: {total_energy:,}")
            print(f"   总可用带宽: {total_bandwidth:,}")
        
        if failed_results:
            print(f"\n查询失败的钱包:")
            for result in failed_results:
                wallet = result['wallet_info']
                print(f"   {wallet['address']} - {result.get('error', '未知错误')}")
        
        if self.network == 'shasta':
            print(f"\n获取免费测试TRX和USDT:")
            print(f"   TRX: 关注 Twitter @TronTest2，发推文: \"@TronTest2 [你的钱包地址]\"")
            print(f"   USDT: 加入TRON Discord，在faucets频道使用: \"!shasta_usdt [你的钱包地址]\"")
            print(f"   Discord: https://discord.gg/GsRgsTD")
            print(f"   每24小时可获得5000测试USDT")
            
            zero_balance_wallets = [r for r in successful_results 
                                  if r['balance_info']['trx_balance'] == 0]
            if zero_balance_wallets:
                print(f"\n需要充值的钱包地址:")
                for result in zero_balance_wallets:
                    print(f"   {result['wallet_info']['address']}")
        
        print(f"\n查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
    
    def save_text_report(self, results: List[Dict[str, Any]], filename: str = 'wallet_report.txt'):
        """保存文本格式的报告"""
        try:
            file_path = os.path.join(self.script_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"TRON {self.network.upper()} 钱包余额查询报告\n")
                f.write("="*80 + "\n\n")
                f.write(f"查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"网络: {self.network.upper()}\n")
                f.write(f"总钱包数: {len(results)}\n\n")
                
                successful_results = [r for r in results if r['status'] == 'success']
                
                for i, result in enumerate(successful_results, 1):
                    wallet = result['wallet_info']
                    balance = result['balance_info']
                    
                    f.write(f"钱包 #{i}\n")
                    f.write(f"地址: {wallet['address']}\n")
                    f.write(f"TRX余额: {balance['trx_balance']:.6f}\n")
                    f.write(f"USDT余额: {balance.get('usdt_balance', 0):.6f}\n")  # 新增USDT
                    f.write(f"可用能量: {balance['energy_available']:,}\n")
                    f.write(f"可用带宽: {balance['bandwidth_available']:,}\n")
                    f.write("-" * 50 + "\n\n")
            
            print(f"查询结果已保存到: {file_path}")
            return file_path
            
        except Exception as e:
            print(f"保存文本报告失败: {e}")
            return None


def main():
    """主函数"""
    print("TRON钱包余额查询工具")
    print("="*50)
    
    # 创建查询器（默认使用Shasta测试网）
    checker = WalletChecker(network="shasta")
    
    try:
        # 查询所有钱包
        results = checker.check_all_wallets()
        
        if not results:
            print("没有钱包可查询")
            return 1
        
        # 保存结果
        checker.save_results(results)
        
        # 生成摘要报告
        checker.generate_summary_report(results)
        
        # 保存文本报告
        checker.save_text_report(results)
        
        print(f"\n查询完成!")
        
    except Exception as e:
        print(f"\n操作失败: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())