# TRON Shasta测试网钱包工具

这是一套完整的TRON Shasta测试网钱包生成和管理工具，包含钱包生成、余额查询、能量/带宽监控等功能。

## 📁 文件结构

```
test-wallets/
├── wallet_generator.py     # 钱包生成工具
├── wallet_checker.py       # 余额查询工具
├── wallets.json           # 生成的钱包信息（包含私钥，请妥善保管）
├── balance_results.json   # 详细余额查询结果
├── wallet_report.txt      # 简化余额报告
└── README.md              # 本说明文档
```

## 🚀 快速开始

### 1. 生成测试钱包

运行钱包生成器创建3个Shasta测试网钱包：

```bash
cd test-wallets
python wallet_generator.py
```

**输出示例：**
```
TRON Shasta测试网钱包生成器
==================================================
成功连接到 TRON Shasta 测试网
开始生成 3 个TRON钱包...

生成第 1 个钱包:
生成钱包: TCX13dZVJt1uCDCGA3F26KqEndpsSt2CHy

生成第 2 个钱包:
生成钱包: TAcrAuU78UyPZpZuVPCQo2ZVcfwmkskWLz

生成第 3 个钱包:
生成钱包: TVAcKMkSvL8Jbf58AKLnWFesYjiznNUnr4

成功生成 3 个钱包!
```

### 2. 查询钱包余额

运行余额查询工具检查所有钱包的状态：

```bash
python wallet_checker.py
```

**输出示例：**
```
TRON钱包余额查询工具
==================================================
连接到 TRON SHASTA 网络
成功加载 3 个钱包

开始查询 3 个钱包的余额信息...

[1/3] 查询钱包: TCX13dZVJt1uCDCGA3F26KqEndpsSt2CHy
查询成功 - TRX: 0.000000

[2/3] 查询钱包: TAcrAuU78UyPZpZuVPCQo2ZVcfwmkskWLz  
查询成功 - TRX: 0.000000

[3/3] 查询钱包: TVAcKMkSvL8Jbf58AKLnWFesYjiznNUnr4
查询成功 - TRX: 0.000000
```

## 💰 获取免费测试TRX

新生成的钱包余额为零，需要获取测试TRX才能进行后续测试：

### 方法1：Twitter水龙头 (推荐)

1. **关注** Twitter [@TronTest2](https://twitter.com/TronTest2)
2. **发推文**：`@TronTest2 你的钱包地址`
   
   示例：`@TronTest2 TCX13dZVJt1uCDCGA3F26KqEndpsSt2CHy`

3. **等待5分钟**即可收到 **10,000测试TRX**

### 方法2：Discord水龙头

1. 加入[TRON Discord社区](https://discord.gg/tron)
2. 在 `#faucet` 频道输入：`!shasta [钱包地址]`
3. 即可获得测试TRX

## 📊 生成的钱包信息

### 当前生成的3个测试钱包：

1. **钱包#1**: `TCX13dZVJt1uCDCGA3F26KqEndpsSt2CHy`
2. **钱包#2**: `TAcrAuU78UyPZpZuVPCQo2ZVcfwmkskWLz`  
3. **钱包#3**: `TVAcKMkSvL8Jbf58AKLnWFesYjiznNUnr4`

### 余额状态（最后查询时间：2025-09-11 01:10:20）

| 钱包 | TRX余额 | Energy | Bandwidth | 状态 |
|-----|---------|--------|-----------|------|
| #1  | 0.000000| 0      | 0         | 需要充值 |
| #2  | 0.000000| 0      | 0         | 需要充值 |
| #3  | 0.000000| 0      | 0         | 需要充值 |

## 🔧 工具功能

### wallet_generator.py
- 连接到Shasta测试网
- 生成随机TRON钱包
- 保存钱包信息到JSON文件
- 显示详细的生成报告

### wallet_checker.py  
- 从JSON文件加载钱包信息
- 查询每个钱包的完整余额信息
- 生成详细的查询报告
- 保存结果到多种格式

## 📋 查询结果文件

### balance_results.json
包含完整的查询结果，格式如下：
```json
{
  "query_time": "2025-09-11T01:10:20.303666",
  "network": "shasta", 
  "total_wallets": 3,
  "successful_queries": 3,
  "failed_queries": 0,
  "results": [
    {
      "wallet_info": {
        "address": "TCX13dZVJt1uCDCGA3F26KqEndpsSt2CHy",
        "private_key": "...",
        "public_key": "...",
        "created_at": "2025-09-11T01:09:19.069938",
        "network": "Shasta Testnet"
      },
      "balance_info": {
        "trx_balance": 0,
        "energy_limit": 0,
        "energy_used": 0,
        "energy_available": 0,
        "bandwidth_limit": 0,
        "bandwidth_used": 0,
        "bandwidth_available": 0,
        "free_net_limit": 1500,
        "free_net_used": 0
      },
      "query_time": "2025-09-11T01:10:20.303666",
      "network": "shasta",
      "status": "success"
    }
  ]
}
```

### wallet_report.txt
简化的文本格式报告，便于查看和分享。

## 🔗 相关链接

- **Shasta测试网浏览器**: https://shasta.tronex.io/
- **TRON开发者文档**: https://developers.tron.network/
- **TronPy库文档**: https://tronpy.readthedocs.io/
- **Twitter水龙头**: [@TronTest2](https://twitter.com/TronTest2)

## ⚠️ 安全提醒

1. **测试网专用**：这些钱包仅用于Shasta测试网，不要在主网使用
2. **私钥安全**：`wallets.json`包含私钥信息，请妥善保管，不要分享
3. **测试目的**：仅用于开发和测试，不要存储真实价值的资产
4. **定期备份**：建议定期备份钱包文件和查询结果

## 🛠️ 技术细节

### 依赖库
- `tronpy==0.4.0` - TRON Python客户端
- 项目现有的 `tron_api.py` 模块

### 网络配置
- **网络**: Shasta测试网
- **官方API**: `https://api.shasta.trongrid.io`
- **TronScan API**: `https://shastapi.tronscan.org`

### 支持的查询信息
- TRX余额（SUN单位转换为TRX）
- Energy总限制/已使用/可用
- Bandwidth总限制/已使用/可用  
- 免费带宽使用情况
- 账户创建时间
- 查询成功率统计

## 📞 下一步

1. **充值测试TRX**：使用Twitter水龙头为钱包充值
2. **测试转账**：在钱包间进行测试转账
3. **能量租赁测试**：使用主项目的能量租赁功能
4. **智能合约交互**：部署和测试智能合约

---

*生成时间：2025-09-11 01:09:19*  
*最后更新：2025-09-11 01:10:20*