#!/usr/bin/env python3
"""
TRON API连接测试脚本
测试Shasta测试网API连接和余额查询功能
"""

import sys
sys.path.append('.')

from tron_api import TronAPI
import json

def test_tron_api():
    """测试TRON API连接和功能"""
    print("TRON API连接测试开始...")
    print("=" * 50)
    
    # 初始化API客户端 (Shasta测试网)
    api = TronAPI(network="shasta")
    print(f"API客户端初始化成功 - 网络: {api.network}")
    print(f"API URL: {api.api_url}")
    print(f"TronScan URL: {api.tronscan_url}")
    print()
    
    # 测试钱包地址
    test_addresses = [
        "TCX13dZVJt1uCDCGA3F26KqEndpsSt2CHy",  # 钱包#1
        "TAcrAuU78UyPZpZuVPCQo2ZVcfwmkskWLz",  # 钱包#2  
        "TVAcKMkSvL8Jbf58AKLnWFesYjiznNUnr4",  # 钱包#3
    ]
    
    results = []
    
    for i, address in enumerate(test_addresses, 1):
        print(f"测试钱包#{i}: {address}")
        print("-" * 30)
        
        # 测试地址验证
        is_valid = api.is_valid_address(address)
        print(f"地址格式验证: {'有效' if is_valid else '无效'}")
        
        if not is_valid:
            results.append({
                "wallet": i,
                "address": address,
                "valid": False,
                "balance": None,
                "error": "地址格式无效"
            })
            print()
            continue
        
        # 测试余额查询
        try:
            balance = api.get_account_balance(address)
            if balance:
                print(f"余额查询成功")
                print(f"  TRX余额: {balance.trx_balance:.6f}")
                print(f"  Energy可用: {balance.energy_available}")
                print(f"  Bandwidth可用: {balance.bandwidth_available}")
                
                results.append({
                    "wallet": i,
                    "address": address,
                    "valid": True,
                    "balance": {
                        "trx": balance.trx_balance,
                        "energy": balance.energy_available,
                        "bandwidth": balance.bandwidth_available
                    },
                    "error": None
                })
            else:
                print("余额查询失败")
                results.append({
                    "wallet": i,
                    "address": address,  
                    "valid": True,
                    "balance": None,
                    "error": "余额查询失败"
                })
                
        except Exception as e:
            print(f"查询异常: {e}")
            results.append({
                "wallet": i,
                "address": address,
                "valid": True,
                "balance": None,
                "error": str(e)
            })
        
        print()
    
    # 输出测试总结
    print("测试结果总结")
    print("=" * 50)
    
    successful = len([r for r in results if r["balance"] is not None])
    total = len(results)
    
    print(f"总测试地址: {total}")
    print(f"成功查询: {successful}")
    print(f"失败查询: {total - successful}")
    print(f"成功率: {successful/total*100:.1f}%")
    print()
    
    # 保存结果到文件
    with open("api_test_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "test_time": "2025-09-12T12:25:00Z",
            "network": "shasta",
            "api_url": api.api_url,
            "tronscan_url": api.tronscan_url,
            "results": results,
            "summary": {
                "total": total,
                "successful": successful,
                "failed": total - successful,
                "success_rate": successful/total*100
            }
        }, f, indent=2, ensure_ascii=False)
    
    print("测试结果已保存到 api_test_results.json")
    
    return successful == total

if __name__ == "__main__":
    success = test_tron_api()
    if success:
        print("\n所有API测试通过！")
        sys.exit(0)
    else:
        print("\n部分API测试失败")
        sys.exit(1)