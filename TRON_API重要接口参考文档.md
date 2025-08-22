# TRON API 重要接口参考文档

## 概述

本文档汇总了TRON网络中最重要的API接口，包括钱包操作、资源查询、合约交互等核心功能的接口说明和使用示例。

## 1. 账户信息查询接口

### 1.1 获取账户信息 - getAccount

**接口**: `/wallet/getaccount`  
**方法**: POST  
**描述**: 查询账户的基本信息，包括TRX余额、冻结余额、权限等

**请求参数**:
```json
{
  "address": "41E552F6487585C2B58BC2C9BB4492BC1F17132CD0",  // 账户地址(hex格式)
  "visible": true  // 可选，true返回base58格式地址
}
```

**响应示例**:
```json
{
  "address": "TLPpXqEnbRvKuE7CyxSvWtSyJhJnBJKNDj",
  "balance": 29887074430,  // TRX余额(SUN单位)
  "create_time": 1575710031000,
  "latest_opration_time": 1577356614000,
  "frozen": [
    {
      "frozen_balance": 12000000,  // 冻结余额
      "expire_time": 1577615814000  // 到期时间
    }
  ],
  "account_resource": {
    "frozen_balance_for_energy": {
      "frozen_balance": 12000000,
      "expire_time": 1577588400000
    }
  },
  "assetV2": [  // TRC-10代币
    {
      "key": "1000001",
      "value": 1000
    }
  ]
}
```

### 1.2 获取账户资源信息 - getAccountResource

**接口**: `/wallet/getaccountresource`  
**方法**: POST  
**描述**: 查询账户的Energy和Bandwidth资源详情

**请求参数**:
```json
{
  "address": "41E552F6487585C2B58BC2C9BB4492BC1F17132CD0",
  "visible": true
}
```

**响应示例**:
```json
{
  "freeNetLimit": 1500,  // 免费带宽限制
  "freeNetUsed": 557,    // 已使用免费带宽
  "NetLimit": 43200000000,  // 质押获得的带宽限制
  "NetUsed": 0,         // 已使用质押带宽
  "EnergyLimit": 90000000,  // Energy限制
  "EnergyUsed": 13560000,   // 已使用Energy
  "TotalNetLimit": 43200001500,
  "TotalNetWeight": 84593524300,
  "TotalEnergyLimit": 90000000000,
  "TotalEnergyWeight": 1026595479
}
```

### 1.3 获取账户特定区块余额 - getAccountBalance

**接口**: `/wallet/getaccountbalance`  
**方法**: POST  
**描述**: 查询账户在特定区块的余额信息

**请求参数**:
```json
{
  "account_identifier": {
    "address": "41E552F6487585C2B58BC2C9BB4492BC1F17132CD0"
  },
  "block_identifier": {
    "hash": "00000000000000001e8b9a8d9c..."  // 区块hash
  }
}
```

## 2. TRC-20代币接口

### 2.1 查询TRC-20代币余额 - triggerConstantContract

**接口**: `/wallet/triggerconstantcontract`  
**方法**: POST  
**描述**: 调用智能合约的只读方法，主要用于查询TRC-20代币余额

**请求参数**:
```json
{
  "contract_address": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",  // USDT合约地址
  "function_selector": "balanceOf(address)",
  "parameter": "000000000000000000000041E552F6487585C2B58BC2C9BB4492BC1F17132CD0",
  "owner_address": "41E552F6487585C2B58BC2C9BB4492BC1F17132CD0",
  "visible": true
}
```

**Python示例**:
```python
import requests

def get_trc20_balance(contract_address, wallet_address, api_url="https://api.trongrid.io"):
    url = f"{api_url}/wallet/triggerconstantcontract"
    
    # 将地址转换为hex格式并填充参数
    hex_address = wallet_address.replace('T', '41') if wallet_address.startswith('T') else wallet_address
    parameter = "000000000000000000000000" + hex_address[2:]
    
    payload = {
        "contract_address": contract_address,
        "function_selector": "balanceOf(address)",
        "parameter": parameter,
        "owner_address": wallet_address,
        "visible": True
    }
    
    response = requests.post(url, json=payload)
    return response.json()
```

### 2.2 TRC-20代币持有者列表

**接口**: `/api/token/holders`  
**方法**: GET  
**描述**: 获取TRC-20代币的持有者列表和余额

**请求参数**:
```
GET /api/token/holders?contract_address=TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t&limit=20&start=0
```

## 3. 交易接口

### 3.1 创建转账交易 - createTransaction

**接口**: `/wallet/createtransaction`  
**方法**: POST  
**描述**: 创建TRX转账交易

**请求参数**:
```json
{
  "to_address": "41E552F6487585C2B58BC2C9BB4492BC1F17132CD0",
  "owner_address": "41D1E7A6BC354106CB410E65FF8B181C600FF14292",
  "amount": 1000000,  // 转账金额(SUN单位)
  "visible": true
}
```

### 3.2 广播交易 - broadcastTransaction

**接口**: `/wallet/broadcasttransaction`  
**方法**: POST  
**描述**: 广播已签名的交易到网络

**请求参数**:
```json
{
  "signature": ["..."],  // 签名数组
  "txID": "...",        // 交易ID
  "raw_data": {...}     // 原始交易数据
}
```

## 4. 区块和网络信息接口

### 4.1 获取最新区块 - getNowBlock

**接口**: `/wallet/getnowblock`  
**方法**: POST  
**描述**: 获取最新区块信息

### 4.2 获取区块信息 - getBlockByNum

**接口**: `/wallet/getblockbynum`  
**方法**: POST  
**描述**: 根据区块高度获取区块信息

**请求参数**:
```json
{
  "num": 1000  // 区块高度
}
```

### 4.3 获取链参数 - getChainParameters

**接口**: `/wallet/getchainparameters`  
**方法**: POST  
**描述**: 获取链的当前参数，如手续费率等

## 5. 资源租赁相关接口

### 5.1 冻结余额获取资源 - freezeBalance

**接口**: `/wallet/freezebalance`  
**方法**: POST  
**描述**: 冻结TRX获取Energy或Bandwidth

**请求参数**:
```json
{
  "owner_address": "41E552F6487585C2B58BC2C9BB4492BC1F17132CD0",
  "frozen_balance": 1000000,  // 冻结金额(SUN)
  "frozen_duration": 3,       // 冻结天数
  "resource": "ENERGY",       // 资源类型: ENERGY 或 BANDWIDTH
  "visible": true
}
```

### 5.2 解冻余额 - unfreezeBalance

**接口**: `/wallet/unfreezebalance`  
**方法**: POST  
**描述**: 解冻TRX，释放资源

### 5.3 委托资源 - delegateResource

**接口**: `/wallet/delegateresource`  
**方法**: POST  
**描述**: 将资源委托给其他地址（能量租赁的核心接口）

**请求参数**:
```json
{
  "owner_address": "41E552F6487585C2B58BC2C9BB4492BC1F17132CD0",
  "receiver_address": "41D1E7A6BC354106CB410E65FF8B181C600FF14292",
  "balance": 1000000,     // 委托的TRX数量
  "resource": "ENERGY",   // 委托的资源类型
  "lock": true,          // 是否锁定
  "lock_period": 86400,  // 锁定期间(秒)
  "visible": true
}
```

### 5.4 取消委托资源 - unDelegateResource

**接口**: `/wallet/undelegateresource`  
**方法**: POST  
**描述**: 取消资源委托

## 6. 第三方API接口

### 6.1 TronScan API

**基础URL**: `https://apilist.tronscan.org`

#### 6.1.1 获取账户详情
```
GET /api/account?address={address}&includeToken=true
```

**响应包含**:
- TRX余额
- TRC-20代币余额列表
- TRC-10代币余额
- 交易统计

#### 6.1.2 获取代币信息
```
GET /api/token_trc20?contract={contract_address}
```

### 6.2 TronGrid API

**基础URL**: `https://api.trongrid.io`  
**认证**: 需要API Key

```python
headers = {
    'TRON-PRO-API-KEY': 'your-api-key'
}
```

## 7. 使用示例和最佳实践

### 7.1 完整的余额查询示例

```python
import requests
import json

class TronAPI:
    def __init__(self, api_url="https://api.trongrid.io", api_key=None):
        self.api_url = api_url
        self.headers = {'TRON-PRO-API-KEY': api_key} if api_key else {}
    
    def get_account_info(self, address):
        """获取账户基本信息"""
        url = f"{self.api_url}/wallet/getaccount"
        payload = {"address": address, "visible": True}
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()
    
    def get_account_resources(self, address):
        """获取账户资源信息"""
        url = f"{self.api_url}/wallet/getaccountresource"
        payload = {"address": address, "visible": True}
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()
    
    def get_trc20_balance(self, contract_address, wallet_address):
        """获取TRC-20代币余额"""
        url = f"{self.api_url}/wallet/triggerconstantcontract"
        
        # 地址格式转换
        if wallet_address.startswith('T'):
            hex_address = wallet_address  # TronGrid支持base58
        
        payload = {
            "contract_address": contract_address,
            "function_selector": "balanceOf(address)",
            "parameter": f"000000000000000000000000{wallet_address[1:]}",
            "owner_address": wallet_address,
            "visible": True
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()

# 使用示例
tron = TronAPI(api_key="your-api-key")
address = "TLPpXqEnbRvKuE7CyxSvWtSyJhJnBJKNDj"

# 获取TRX余额
account_info = tron.get_account_info(address)
trx_balance = account_info.get('balance', 0) / 1000000  # 转换为TRX

# 获取Energy和Bandwidth
resources = tron.get_account_resources(address)
available_energy = resources.get('EnergyLimit', 0) - resources.get('EnergyUsed', 0)

# 获取USDT余额
usdt_contract = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
usdt_balance = tron.get_trc20_balance(usdt_contract, address)
```

### 7.2 错误处理

```python
def safe_api_call(func, *args, **kwargs):
    """安全的API调用包装器"""
    try:
        response = func(*args, **kwargs)
        if 'Error' in response:
            print(f"API错误: {response['Error']}")
            return None
        return response
    except requests.exceptions.RequestException as e:
        print(f"网络错误: {e}")
        return None
    except Exception as e:
        print(f"未知错误: {e}")
        return None
```

## 8. 重要说明

### 8.1 API限制
- **TronGrid**: 需要API Key，有调用频率限制
- **公共节点**: 免费但有严格的调用限制
- **建议**: 生产环境使用付费API Key

### 8.2 地址格式
- **Base58**: `TLPpXqEnbRvKuE7CyxSvWtSyJhJnBJKNDj`
- **Hex**: `41E552F6487585C2B58BC2C9BB4492BC1F17132CD0`
- **转换**: 使用`visible: true`参数统一返回Base58格式

### 8.3 数值单位
- **TRX**: 1 TRX = 1,000,000 SUN
- **Energy**: 直接使用返回值
- **代币**: 注意小数位数(decimals)

### 8.4 网络选择
- **主网**: `https://api.trongrid.io`
- **Shasta测试网**: `https://api.shasta.trongrid.io`
- **Nile测试网**: `https://nile.trongrid.io`

这份文档涵盖了TRON网络开发中最常用的API接口，特别适合能量租赁机器人项目的开发需求。