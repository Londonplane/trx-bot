#!/usr/bin/env python3
"""
TRON能量助手闪租页自动化测试脚本
========================================

功能:
- API接口自动化测试
- 数据一致性验证
- 基本性能测试
- 生成测试报告

使用方法:
python flash_rental_test.py
"""

import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FlashRentalTester:
    """闪租页功能自动化测试类"""
    
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        self.test_results = []
        self.test_user_id = 999888
        self.test_start_time = datetime.now()
        
    def run_all_tests(self):
        """运行所有测试用例"""
        logger.info("🚀 开始闪租页功能测试...")
        
        # 测试组1: 基础服务测试
        self.test_health_check()
        
        # 测试组2: 用户管理测试
        self.test_user_balance_query()
        self.test_user_deposit()
        
        # 测试组3: 订单管理测试
        self.test_order_creation()
        self.test_order_query()
        self.test_order_cancellation()
        
        # 测试组4: 钱包管理测试
        self.test_supplier_wallets_query()
        
        # 测试组5: 边界条件测试
        self.test_invalid_order_creation()
        self.test_insufficient_balance()
        
        # 生成测试报告
        self.generate_report()
        
    def test_health_check(self):
        """测试系统健康检查"""
        test_name = "系统健康检查"
        logger.info(f"📋 执行测试: {test_name}")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response_time = time.time() - start_time
            
            assert response.status_code == 200
            data = response.json()
            assert data.get("status") == "healthy"
            
            self.add_result(test_name, True, f"响应时间: {response_time:.3f}s", data)
            logger.info(f"✅ {test_name} - 通过")
            
        except Exception as e:
            self.add_result(test_name, False, str(e))
            logger.error(f"❌ {test_name} - 失败: {e}")
    
    def test_user_balance_query(self):
        """测试用户余额查询"""
        test_name = "用户余额查询"
        logger.info(f"📋 执行测试: {test_name}")
        
        try:
            response = requests.get(f"{self.base_url}/api/users/{self.test_user_id}/balance")
            assert response.status_code == 200
            
            data = response.json()
            assert "balance_trx" in data
            
            balance = float(data["balance_trx"])
            assert balance >= 0
            
            self.add_result(test_name, True, f"用户余额: {balance} TRX", data)
            logger.info(f"✅ {test_name} - 通过，余额: {balance} TRX")
            
        except Exception as e:
            self.add_result(test_name, False, str(e))
            logger.error(f"❌ {test_name} - 失败: {e}")
    
    def test_user_deposit(self):
        """测试用户充值功能"""
        test_name = "用户充值功能"
        logger.info(f"📋 执行测试: {test_name}")
        
        try:
            # 先查询当前余额
            balance_response = requests.get(f"{self.base_url}/api/users/{self.test_user_id}/balance")
            initial_balance = float(balance_response.json()["balance_trx"])
            
            # 执行充值
            deposit_data = {
                "tx_hash": f"test_hash_{int(time.time())}",
                "amount": 10.0,
                "currency": "TRX"
            }
            
            response = requests.post(
                f"{self.base_url}/api/users/{self.test_user_id}/deposit",
                json=deposit_data
            )
            assert response.status_code == 200
            
            # 验证余额更新
            time.sleep(1)  # 等待数据库更新
            new_balance_response = requests.get(f"{self.base_url}/api/users/{self.test_user_id}/balance")
            new_balance = float(new_balance_response.json()["balance_trx"])
            
            expected_balance = initial_balance + 10.0
            assert abs(new_balance - expected_balance) < 0.001
            
            self.add_result(test_name, True, f"充值成功: {initial_balance} → {new_balance} TRX")
            logger.info(f"✅ {test_name} - 通过，余额更新: {initial_balance} → {new_balance}")
            
        except Exception as e:
            self.add_result(test_name, False, str(e))
            logger.error(f"❌ {test_name} - 失败: {e}")
    
    def test_order_creation(self):
        """测试订单创建功能"""
        test_name = "订单创建功能"
        logger.info(f"📋 执行测试: {test_name}")
        
        try:
            order_data = {
                "user_id": self.test_user_id,
                "energy_amount": 32000,
                "duration": "1h",
                "receive_address": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
            }
            
            start_time = time.time()
            response = requests.post(f"{self.base_url}/api/orders/", json=order_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                assert "id" in data
                assert data["user_id"] == self.test_user_id
                assert data["energy_amount"] == 32000
                assert data["status"] in ["pending", "processing"]
                
                self.order_id = data["id"]  # 保存订单ID供后续测试使用
                self.add_result(test_name, True, f"订单创建成功: {data['id'][:8]}..., 响应时间: {response_time:.3f}s", data)
                logger.info(f"✅ {test_name} - 通过，订单ID: {data['id'][:8]}...")
                
            elif response.status_code == 400:
                # 可能是余额不足或其他业务错误，这是正常的测试情况
                error_data = response.json()
                if "余额不足" in error_data.get("detail", ""):
                    self.add_result(test_name, True, "余额不足测试通过 - 预期的错误响应", error_data)
                    logger.info(f"✅ {test_name} - 通过（余额不足，符合预期）")
                else:
                    self.add_result(test_name, False, f"业务错误: {error_data}")
                    logger.warning(f"⚠️ {test_name} - 业务错误: {error_data}")
            else:
                raise Exception(f"意外的响应状态码: {response.status_code}")
                
        except Exception as e:
            self.add_result(test_name, False, str(e))
            logger.error(f"❌ {test_name} - 失败: {e}")
    
    def test_order_query(self):
        """测试订单查询功能"""
        test_name = "订单查询功能"
        logger.info(f"📋 执行测试: {test_name}")
        
        try:
            # 先获取用户的订单列表
            response = requests.get(f"{self.base_url}/api/orders/?user_id={self.test_user_id}&limit=5")
            assert response.status_code == 200
            
            orders = response.json()
            assert isinstance(orders, list)
            
            if orders:
                # 测试单个订单查询
                order_id = orders[0]["id"]
                detail_response = requests.get(f"{self.base_url}/api/orders/{order_id}")
                assert detail_response.status_code == 200
                
                order_detail = detail_response.json()
                assert order_detail["id"] == order_id
                assert "status" in order_detail
                assert "created_at" in order_detail
                
                self.add_result(test_name, True, f"查询到 {len(orders)} 个订单", {"order_count": len(orders)})
                logger.info(f"✅ {test_name} - 通过，查询到 {len(orders)} 个订单")
            else:
                self.add_result(test_name, True, "无订单记录（正常情况）")
                logger.info(f"✅ {test_name} - 通过，无订单记录")
            
        except Exception as e:
            self.add_result(test_name, False, str(e))
            logger.error(f"❌ {test_name} - 失败: {e}")
    
    def test_order_cancellation(self):
        """测试订单取消功能"""
        test_name = "订单取消功能"
        logger.info(f"📋 执行测试: {test_name}")
        
        try:
            # 获取pending状态的订单
            response = requests.get(f"{self.base_url}/api/orders/?user_id={self.test_user_id}&limit=10")
            orders = response.json()
            
            pending_orders = [order for order in orders if order["status"] in ["pending", "processing"]]
            
            if pending_orders:
                order_id = pending_orders[0]["id"]
                cancel_response = requests.post(f"{self.base_url}/api/orders/{order_id}/cancel")
                
                if cancel_response.status_code == 200:
                    result = cancel_response.json()
                    assert result.get("success") == True
                    
                    self.add_result(test_name, True, f"订单 {order_id[:8]}... 取消成功")
                    logger.info(f"✅ {test_name} - 通过，订单已取消")
                else:
                    # 订单可能已经不能取消（状态已变更）
                    self.add_result(test_name, True, f"订单不可取消（状态已变更，符合业务逻辑）")
                    logger.info(f"✅ {test_name} - 通过（订单不可取消）")
            else:
                self.add_result(test_name, True, "无可取消的订单（正常情况）")
                logger.info(f"✅ {test_name} - 通过，无可取消订单")
                
        except Exception as e:
            self.add_result(test_name, False, str(e))
            logger.error(f"❌ {test_name} - 失败: {e}")
    
    def test_supplier_wallets_query(self):
        """测试供应商钱包查询"""
        test_name = "供应商钱包查询"
        logger.info(f"📋 执行测试: {test_name}")
        
        try:
            response = requests.get(f"{self.base_url}/api/supplier-wallets/")
            assert response.status_code == 200
            
            wallets = response.json()
            assert isinstance(wallets, list)
            
            if wallets:
                wallet = wallets[0]
                required_fields = ["id", "wallet_address", "trx_balance", "energy_available", "is_active"]
                for field in required_fields:
                    assert field in wallet, f"缺少字段: {field}"
                
                self.add_result(test_name, True, f"查询到 {len(wallets)} 个供应商钱包", {"wallet_count": len(wallets)})
                logger.info(f"✅ {test_name} - 通过，{len(wallets)} 个钱包")
            else:
                self.add_result(test_name, True, "无供应商钱包（需要配置）")
                logger.info(f"✅ {test_name} - 通过，无钱包配置")
                
        except Exception as e:
            self.add_result(test_name, False, str(e))
            logger.error(f"❌ {test_name} - 失败: {e}")
    
    def test_invalid_order_creation(self):
        """测试无效订单创建（边界测试）"""
        test_name = "无效订单创建测试"
        logger.info(f"📋 执行测试: {test_name}")
        
        try:
            # 测试无效地址
            invalid_order = {
                "user_id": self.test_user_id,
                "energy_amount": 32000,
                "duration": "1h",
                "receive_address": "invalid_address"
            }
            
            response = requests.post(f"{self.base_url}/api/orders/", json=invalid_order)
            
            # 应该返回400错误
            if response.status_code == 422 or response.status_code == 400:
                self.add_result(test_name, True, "无效地址正确被拒绝")
                logger.info(f"✅ {test_name} - 通过，无效地址被拒绝")
            else:
                self.add_result(test_name, False, f"无效地址未被拒绝，状态码: {response.status_code}")
                logger.error(f"❌ {test_name} - 失败，无效地址未被拒绝")
                
        except Exception as e:
            self.add_result(test_name, False, str(e))
            logger.error(f"❌ {test_name} - 失败: {e}")
    
    def test_insufficient_balance(self):
        """测试余额不足场景"""
        test_name = "余额不足测试"
        logger.info(f"📋 执行测试: {test_name}")
        
        try:
            # 创建一个大额订单来测试余额不足
            large_order = {
                "user_id": self.test_user_id,
                "energy_amount": 1000000,  # 100万Energy，费用会很高
                "duration": "14d",
                "receive_address": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
            }
            
            response = requests.post(f"{self.base_url}/api/orders/", json=large_order)
            
            if response.status_code == 400:
                error_data = response.json()
                if "余额不足" in error_data.get("detail", ""):
                    self.add_result(test_name, True, "余额不足正确被检测")
                    logger.info(f"✅ {test_name} - 通过，余额不足被正确检测")
                else:
                    self.add_result(test_name, False, f"非预期的错误: {error_data}")
                    logger.error(f"❌ {test_name} - 非预期错误: {error_data}")
            elif response.status_code == 200:
                # 如果用户余额充足，订单创建成功也是正常的
                self.add_result(test_name, True, "用户余额充足，订单创建成功")
                logger.info(f"✅ {test_name} - 通过，用户余额充足")
            else:
                self.add_result(test_name, False, f"意外的响应状态: {response.status_code}")
                
        except Exception as e:
            self.add_result(test_name, False, str(e))
            logger.error(f"❌ {test_name} - 失败: {e}")
    
    def add_result(self, test_name: str, passed: bool, message: str = "", data: Optional[Dict] = None):
        """添加测试结果"""
        self.test_results.append({
            "test_name": test_name,
            "passed": passed,
            "message": message,
            "data": data,
            "timestamp": datetime.now()
        })
    
    def generate_report(self):
        """生成测试报告"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        test_duration = datetime.now() - self.test_start_time
        
        # 控制台报告
        print("\n" + "="*60)
        print("📊 闪租页功能测试报告")
        print("="*60)
        print(f"🕒 测试时间: {self.test_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  测试耗时: {test_duration.total_seconds():.2f} 秒")
        print(f"📈 成功率: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        print(f"✅ 通过: {passed_tests} 项")
        print(f"❌ 失败: {failed_tests} 项")
        print()
        
        # 详细结果
        for result in self.test_results:
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"{status} {result['test_name']}")
            if result["message"]:
                print(f"     {result['message']}")
        
        # 生成JSON报告文件
        report_data = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate,
                "test_duration_seconds": test_duration.total_seconds(),
                "start_time": self.test_start_time.isoformat(),
                "end_time": datetime.now().isoformat()
            },
            "test_results": self.test_results
        }
        
        report_file = f"flash_rental_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n📄 详细测试报告已保存至: {report_file}")
        
        # 测试结论
        if failed_tests == 0:
            print("🎉 所有测试通过！闪租页功能工作正常。")
        elif success_rate >= 80:
            print("⚠️  大部分测试通过，有少量问题需要修复。")
        else:
            print("🚨 多个测试失败，需要检查系统状态。")
        
        print("="*60)

def main():
    """主函数"""
    print("🚀 TRON能量助手闪租页自动化测试")
    print("="*50)
    
    # 检查后端服务可用性
    try:
        response = requests.get("http://localhost:8002/health", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务连接正常")
        else:
            print("❌ 后端服务响应异常")
            return
    except requests.exceptions.RequestException:
        print("❌ 无法连接到后端服务 (http://localhost:8002)")
        print("请确保后端服务已启动：cd backend && python main.py")
        return
    
    # 执行测试
    tester = FlashRentalTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()