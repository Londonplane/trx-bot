#!/usr/bin/env python3
"""
测试价格调整后的效果
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import calculate_mock_cost

def test_price_calculation():
    """测试价格计算"""
    print("价格调整测试（已乘以20倍）")
    print("=" * 50)
    
    # 测试不同能量和时长的组合
    test_cases = [
        ("65K", "1h"),
        ("135K", "1d"),
        ("270K", "3d"),
        ("540K", "7d"),
        ("1M", "14d"),
    ]
    
    for energy, duration in test_cases:
        cost = calculate_mock_cost(energy, duration)
        print(f"能量: {energy:>5} | 时长: {duration:>3} | 价格: {cost:>8} TRX")
    
    print("\n" + "=" * 50)
    print("价格已按要求调整为原来的20倍")

if __name__ == "__main__":
    test_price_calculation()