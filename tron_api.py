import requests
import json
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class AccountBalance:
    """账户余额数据类"""
    address: str
    trx_balance: float  # TRX余额 
    energy_limit: int   # Energy总限制
    energy_used: int    # 已使用Energy
    energy_available: int  # 可用Energy
    bandwidth_limit: int   # Bandwidth总限制  
    bandwidth_used: int    # 已使用Bandwidth
    bandwidth_available: int  # 可用Bandwidth
    free_net_limit: int    # 免费带宽限制
    free_net_used: int     # 已使用免费带宽

class TronAPI:
    """TRON API客户端"""
    
    def __init__(self, api_url: str = "https://api.trongrid.io", api_key: Optional[str] = None, network: str = "mainnet"):
        """
        初始化TRON API客户端
        
        Args:
            api_url: API地址，默认为主网
            api_key: API密钥（可选）
            network: 网络类型 ("mainnet", "shasta", "nile")
        """
        # 根据网络类型设置API URL
        if network.lower() == "shasta":
            self.api_url = "https://api.shasta.trongrid.io"
            self.tronscan_url = "https://shastapi.tronscan.org"
        elif network.lower() == "nile":
            self.api_url = "https://nile.trongrid.io"  
            self.tronscan_url = "https://nileapi.tronscan.org"
        else:
            # 主网
            self.api_url = api_url.rstrip('/')
            self.tronscan_url = "https://apilist.tronscan.org"
        
        self.network = network.lower()
        self.headers = {'Content-Type': 'application/json'}
        if api_key:
            self.headers['TRON-PRO-API-KEY'] = api_key
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"初始化TRON API客户端 - 网络: {self.network}, URL: {self.api_url}")
    
    def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """发起API请求"""
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        
        try:
            self.logger.debug(f"请求URL: {url}")
            self.logger.debug(f"请求参数: {payload}")
            
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            self.logger.debug(f"响应数据: {result}")
            
            # 检查各种错误情况
            if 'Error' in result:
                self.logger.error(f"API错误: {result['Error']}")
                return None
            
            if 'error' in result:
                self.logger.error(f"API错误: {result['error']}")
                return None
                
            # 检查是否为空账户（账户不存在）
            if endpoint.endswith('getaccount') and not result:
                self.logger.error("账户不存在或未激活")
                return None
                
            return result
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"网络请求错误: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析错误: {e}")
            return None
        except Exception as e:
            self.logger.error(f"未知错误: {e}")
            return None
    
    def is_valid_address(self, address: str) -> bool:
        """验证TRON地址是否有效"""
        if not address:
            return False
        
        # 基本格式检查
        if address.startswith('T') and len(address) == 34:
            return True
        elif len(address) == 42 and address.startswith('41'):
            return True
        
        return False
    
    def get_account_info(self, address: str) -> Optional[Dict[str, Any]]:
        """获取账户基本信息"""
        if not self.is_valid_address(address):
            self.logger.error(f"无效的地址格式: {address}")
            return None
        
        payload = {
            "address": address,
            "visible": True
        }
        
        return self._make_request("/wallet/getaccount", payload)
    
    def get_account_resources(self, address: str) -> Optional[Dict[str, Any]]:
        """获取账户资源信息"""
        if not self.is_valid_address(address):
            self.logger.error(f"无效的地址格式: {address}")
            return None
        
        payload = {
            "address": address,
            "visible": True
        }
        
        return self._make_request("/wallet/getaccountresource", payload)
    
    def get_account_balance_tronscan(self, address: str) -> Optional[AccountBalance]:
        """使用TronScan API获取账户余额（备用方案）"""
        try:
            url = f"{self.tronscan_url}/api/account?address={address}&includeToken=false"
            headers = {"accept": "application/json"}
            
            self.logger.debug(f"TronScan查询URL: {url}")
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'error' in data:
                self.logger.error(f"TronScan API错误: {data['error']}")
                return None
            
            # 解析数据
            balance_data = data.get('balance', 0)
            trx_balance = balance_data / 1_000_000 if balance_data else 0
            
            # TronScan返回的资源信息
            bandwidth_data = data.get('bandwidth', {})
            energy_data = data.get('energy', {})
            
            # 解析带宽
            free_bandwidth_limit = bandwidth_data.get('freeNetLimit', 1500)
            free_bandwidth_used = bandwidth_data.get('freeNetUsed', 0)
            net_limit = bandwidth_data.get('netLimit', 0)
            net_used = bandwidth_data.get('netUsed', 0)
            
            total_bandwidth_limit = free_bandwidth_limit + net_limit
            total_bandwidth_used = free_bandwidth_used + net_used
            
            # 解析能量
            energy_limit = energy_data.get('energyLimit', 0)
            energy_used = energy_data.get('energyUsed', 0)
            
            balance = AccountBalance(
                address=address,
                trx_balance=trx_balance,
                energy_limit=energy_limit,
                energy_used=energy_used,
                energy_available=max(0, energy_limit - energy_used),
                bandwidth_limit=total_bandwidth_limit,
                bandwidth_used=total_bandwidth_used,
                bandwidth_available=max(0, total_bandwidth_limit - total_bandwidth_used),
                free_net_limit=free_bandwidth_limit,
                free_net_used=free_bandwidth_used
            )
            
            self.logger.info(f"TronScan查询成功 ({self.network}): TRX={trx_balance:.6f}")
            return balance
            
        except Exception as e:
            self.logger.error(f"TronScan API异常: {e}")
            return None
    
    def get_account_balance(self, address: str) -> Optional[AccountBalance]:
        """获取账户完整余额信息"""
        self.logger.info(f"查询地址余额: {address}")
        
        # 首先尝试官方API（数据更准确和及时，特别是质押信息）
        balance = self.get_account_balance_official(address)
        if balance:
            return balance
        
        # 官方API失败，尝试TronScan API作为备用
        return self.get_account_balance_tronscan(address)
    
    def get_account_balance_official(self, address: str) -> Optional[AccountBalance]:
        """使用官方API获取账户余额"""
        # 获取基本账户信息
        account_info = self.get_account_info(address)
        if not account_info:
            self.logger.error("无法获取账户基本信息")
            return None
        
        # 获取资源信息
        resource_info = self.get_account_resources(address)
        if not resource_info:
            self.logger.error("无法获取账户资源信息")
            return None
        
        try:
            # 解析TRX余额 (SUN转TRX)
            trx_balance = account_info.get('balance', 0) / 1_000_000
            
            # 解析Energy信息
            energy_limit = resource_info.get('EnergyLimit', 0)
            energy_used = resource_info.get('EnergyUsed', 0)
            energy_available = max(0, energy_limit - energy_used)
            
            # 解析Bandwidth信息
            # 质押获得的带宽
            net_limit = resource_info.get('NetLimit', 0)
            net_used = resource_info.get('NetUsed', 0)
            
            # 免费带宽
            free_net_limit = resource_info.get('freeNetLimit', 0)
            free_net_used = resource_info.get('freeNetUsed', 0)
            
            # 总带宽 = 免费带宽 + 质押带宽
            total_bandwidth_limit = free_net_limit + net_limit
            total_bandwidth_used = free_net_used + net_used
            bandwidth_available = max(0, total_bandwidth_limit - total_bandwidth_used)
            
            balance = AccountBalance(
                address=address,
                trx_balance=trx_balance,
                energy_limit=energy_limit,
                energy_used=energy_used,
                energy_available=energy_available,
                bandwidth_limit=total_bandwidth_limit,
                bandwidth_used=total_bandwidth_used,
                bandwidth_available=bandwidth_available,
                free_net_limit=free_net_limit,
                free_net_used=free_net_used
            )
            
            self.logger.info(f"余额查询成功: TRX={trx_balance:.6f}, Energy={energy_available}/{energy_limit}, Bandwidth={bandwidth_available}/{total_bandwidth_limit}")
            return balance
            
        except Exception as e:
            self.logger.error(f"解析余额数据时出错: {e}")
            return None
    
    def format_balance_message(self, balance: AccountBalance) -> str:
        """格式化余额信息为用户友好的消息"""
        message = f"""🏦 钱包余额查询结果

📍 地址: `{balance.address}`

💰 TRX余额: **{balance.trx_balance:.6f} TRX**

⚡ 能量(Energy):
• 可用: **{balance.energy_available:,}**
• 总限制: **{balance.energy_limit:,}**
• 已使用: **{balance.energy_used:,}**
• 使用率: **{(balance.energy_used/max(1, balance.energy_limit)*100):.1f}%**

📶 带宽(Bandwidth):
• 可用: **{balance.bandwidth_available:,}**
• 总限制: **{balance.bandwidth_limit:,}**
• 已使用: **{balance.bandwidth_used:,}**
• 使用率: **{(balance.bandwidth_used/max(1, balance.bandwidth_limit)*100):.1f}%**

📊 免费带宽:
• 可用: **{max(0, balance.free_net_limit - balance.free_net_used):,}**
• 总限制: **{balance.free_net_limit:,}**

🕐 查询时间: {self._get_current_time()}"""
        
        return message
    
    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    # 测试主网
    print("测试主网...")
    api_mainnet = TronAPI(network="mainnet")
    test_address_mainnet = "TLPpXqEnbRvKuE7CyxSvWtSyJhJnBJKNDj"
    balance_mainnet = api_mainnet.get_account_balance(test_address_mainnet)
    if balance_mainnet:
        print("✅ 主网余额查询成功!")
        print(api_mainnet.format_balance_message(balance_mainnet))
    else:
        print("❌ 主网余额查询失败!")
    
    print("\n" + "="*60 + "\n")
    
    # 测试Shasta测试网
    print("测试Shasta测试网...")
    api_shasta = TronAPI(network="shasta")
    test_address_shasta = "TYjwikHnA2VvEcCgyQNGkVpiTYxZoDXtyQ"  # 示例Shasta地址
    balance_shasta = api_shasta.get_account_balance(test_address_shasta)
    if balance_shasta:
        print("✅ Shasta测试网余额查询成功!")
        print(api_shasta.format_balance_message(balance_shasta))
    else:
        print("❌ Shasta测试网余额查询失败!")