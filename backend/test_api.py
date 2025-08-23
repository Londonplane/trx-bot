#!/usr/bin/env python3
"""
API测试脚本
用于验证后端API服务的基本功能
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
TEST_USER_ID = 123456
TEST_WALLET = "TQ5kjKLLm9X4L2D1JgogNis6V1YoAm6sv2"

def test_api(name, method, url, data=None, expected_status=200):
    """测试API接口"""
    print(f"\n🧪 测试: {name}")
    print(f"📍 {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        
        print(f"📊 状态码: {response.status_code}")
        
        if response.status_code == expected_status:
            print("✅ 测试通过")
            if response.content:
                result = response.json()
                print(f"📄 响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ 测试失败 - 期望状态码: {expected_status}")
            print(f"📄 响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def main():
    """运行所有API测试"""
    print("🔬 TRON能量助手后端API测试")
    print("=" * 50)
    
    # 测试计数
    total_tests = 0
    passed_tests = 0
    
    # 1. 健康检查
    total_tests += 1
    if test_api("健康检查", "GET", f"{BASE_URL}/health"):
        passed_tests += 1
    
    # 2. 用户余额查询
    total_tests += 1
    if test_api("查询用户余额", "GET", f"{BASE_URL}/api/users/{TEST_USER_ID}/balance"):
        passed_tests += 1
    
    # 3. 添加钱包地址
    total_tests += 1
    wallet_data = {"wallet_address": TEST_WALLET}
    if test_api("添加钱包地址", "POST", f"{BASE_URL}/api/wallets/users/{TEST_USER_ID}", wallet_data):
        passed_tests += 1
    
    # 4. 查询钱包列表
    total_tests += 1
    if test_api("查询钱包列表", "GET", f"{BASE_URL}/api/wallets/users/{TEST_USER_ID}"):
        passed_tests += 1
    
    # 5. 创建订单 (预期会因余额不足失败)
    total_tests += 1
    order_data = {
        "user_id": TEST_USER_ID,
        "energy_amount": 65000,
        "duration": "1h",
        "receive_address": TEST_WALLET
    }
    if test_api("创建订单", "POST", f"{BASE_URL}/api/orders", order_data, expected_status=400):
        passed_tests += 1
    
    # 6. 查询用户订单
    total_tests += 1
    if test_api("查询用户订单", "GET", f"{BASE_URL}/api/orders?user_id={TEST_USER_ID}"):
        passed_tests += 1
    
    # 测试结果总结
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed_tests}/{total_tests} 通过")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！后端API服务正常运行")
        return True
    else:
        print(f"⚠️  有 {total_tests - passed_tests} 个测试失败")
        print("💡 请检查后端服务是否正确启动，数据库是否正常连接")
        return False

if __name__ == "__main__":
    main()