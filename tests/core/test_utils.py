"""
测试工具函数

提供通用的测试辅助功能，包括API调用、结果验证、日志记录等。
"""

import json
import requests
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from .test_config import get_test_config, get_backend_url, get_api_endpoint

class TestResult:
    """测试结果数据类"""
    
    def __init__(self, test_name: str, status: str, details: str, 
                 expected_result: Any = None, actual_result: Any = None):
        self.test_name = test_name
        self.status = status  # PASS, FAIL, SKIP, PARTIAL
        self.details = details
        self.expected_result = expected_result
        self.actual_result = actual_result
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "test_name": self.test_name,
            "status": self.status,
            "details": self.details,
            "expected": self.expected_result,
            "actual": self.actual_result,
            "timestamp": self.timestamp
        }

class TestLogger:
    """测试日志记录器"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.summary = {"passed": 0, "failed": 0, "skipped": 0, "total": 0}
    
    def log(self, test_name: str, status: str, details: str, 
            expected_result: Any = None, actual_result: Any = None):
        """记录测试结果"""
        result = TestResult(test_name, status, details, expected_result, actual_result)
        self.results.append(result)
        
        # 更新统计
        self.summary["total"] += 1
        if status == "PASS":
            self.summary["passed"] += 1
        elif status == "FAIL":
            self.summary["failed"] += 1
        elif status == "SKIP":
            self.summary["skipped"] += 1
        
        # 输出日志
        print(f"[{status}] {test_name}: {details}")
        return result
    
    def get_success_rate(self) -> float:
        """获取成功率"""
        total = self.summary["total"]
        return (self.summary["passed"] / total * 100) if total > 0 else 0.0
    
    def save_results(self, filename: str = None):
        """保存测试结果到文件"""
        if not get_test_config("SAVE_TEST_RESULTS", True):
            return
        
        results_dir = Path(get_test_config("RESULTS_DIR", "tests/results"))
        results_dir.mkdir(parents=True, exist_ok=True)
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_results_{timestamp}.json"
        
        filepath = results_dir / filename
        
        report = {
            "start_time": self.results[0].timestamp if self.results else None,
            "end_time": datetime.now().isoformat(),
            "summary": self.summary,
            "success_rate": f"{self.get_success_rate():.1f}%",
            "tests": [result.to_dict() for result in self.results]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n测试结果已保存到: {filepath}")
        return filepath

class APITester:
    """API测试辅助类"""
    
    def __init__(self, logger: TestLogger = None):
        self.session = requests.Session()
        self.logger = logger or TestLogger()
    
    def test_health_check(self) -> bool:
        """测试后端服务健康状态"""
        try:
            url = get_api_endpoint("health_check")
            timeout = get_test_config("API_TIMEOUT", 10)
            
            response = self.session.get(url, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                self.logger.log("后端健康检查", "PASS", 
                              f"服务正常运行，状态：{data.get('status')}")
                return True
            else:
                self.logger.log("后端健康检查", "FAIL", 
                              f"HTTP状态码：{response.status_code}")
                return False
                
        except Exception as e:
            self.logger.log("后端健康检查", "FAIL", f"连接失败：{str(e)}")
            return False
    
    def make_api_request(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """发起API请求"""
        try:
            timeout = get_test_config("API_TIMEOUT", 10)
            kwargs.setdefault("timeout", timeout)
            
            response = self.session.request(method, url, **kwargs)
            return response
            
        except Exception as e:
            self.logger.log(f"API请求失败", "FAIL", f"{method} {url}: {str(e)}")
            return None

def compare_balance(expected: float, actual: float, tolerance: float = None) -> bool:
    """比较余额数值，允许误差"""
    if tolerance is None:
        tolerance = get_test_config("BALANCE_TOLERANCE", 1.0)
    return abs(actual - expected) <= tolerance

def format_balance_info(balance_info: Dict) -> str:
    """格式化余额信息显示"""
    return f"TRX: {balance_info.get('trx_balance', 0)}, " \
           f"Energy: {balance_info.get('energy_available', 0)}, " \
           f"Bandwidth: {balance_info.get('bandwidth_available', 0)}"

def wait_for_condition(condition_func, timeout: int = 30, interval: float = 1.0) -> bool:
    """等待条件满足"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition_func():
            return True
        time.sleep(interval)
    return False

def create_test_scenario(name: str, description: str, steps: List[str]) -> Dict:
    """创建测试场景定义"""
    return {
        "name": name,
        "description": description,
        "steps": steps,
        "created_at": datetime.now().isoformat()
    }