# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个功能完整的TRON能量助手Telegram机器人项目。机器人实现了钱包管理、余额查询和能量租赁功能，用户可以通过Telegram界面管理TRON钱包地址并查询实时余额信息。

## 核心功能

### 已实现功能
- **钱包管理系统**: 用户可以添加、删除和选择多个TRON钱包地址
- **实时余额查询**: 查询TRX余额、Energy余额和Bandwidth余额
- **闪租页面**: 能量租赁界面，支持参数选择和地址管理
- **地址验证**: 自动验证TRON地址格式
- **双API支持**: 使用TronScan API作为主要接口，官方TRON API作为备用

### 技术特色
- **智能地址管理**: 用户绑定的地址列表，支持添加/选择操作
- **实时API集成**: 真实的TRON区块链数据查询
- **无缝用户体验**: 所有操作通过消息编辑完成，保持上下文
- **完善错误处理**: 网络异常、地址验证、API失败等场景的优雅处理

## 项目架构

### 核心文件结构
```
trx-bot/
├── main.py              # 主程序入口和消息处理
├── buy_energy.py        # 闪租页面逻辑和余额查询
├── models.py            # 数据模型和钱包管理
├── tron_api.py          # TRON API客户端和余额解析
├── config.py            # 配置文件（Bot Token）
└── requirements.txt     # 项目依赖
```

### 关键技术架构
- **会话状态管理**: 内存中存储用户选择和钱包地址
- **API容错机制**: 主API失败时自动切换备用API
- **消息状态同步**: 实时更新消息内容显示余额信息
- **地址验证系统**: 支持Base58和Hex格式的TRON地址

## 用户交互流程

### 1. 闪租页面流程
1. 用户选择能量数量和租用时长
2. 点击"Select address" → 显示钱包管理界面
3. 添加或选择TRON钱包地址
4. 点击"Address balance" → 查询并显示余额信息
5. 显示完整的交易参数和费用计算

### 2. 钱包管理
- **添加地址**: 验证格式并存储到用户会话
- **地址列表**: 显示所有绑定地址，支持选择切换
- **地址验证**: 实时验证TRON地址格式的有效性

### 3. 余额查询
- **多维度信息**: TRX余额、Energy可用量、Bandwidth可用量
- **实时更新**: 点击"Address balance"触发API查询
- **状态提示**: 显示"🔄 Updating balance…"并在完成后删除

## 技术实现

### TRON API集成
- **主要API**: TronScan API (`https://apilist.tronscan.org`)
- **数据解析**: 自动解析TRX、Energy、Bandwidth信息
- **错误处理**: 网络异常、地址未激活等情况的处理

### 数据结构
```python
# 用户会话状态
class UserSession:
    selected_duration: str      # 选择的租用时长
    selected_energy: str        # 选择的能量数量  
    selected_address: str       # 选择的钱包地址
    wallet_addresses: list      # 绑定的钱包地址列表
    address_balance: dict       # 地址余额信息缓存

# 余额数据结构
class AccountBalance:
    trx_balance: float          # TRX余额
    energy_available: int       # 可用Energy
    bandwidth_available: int    # 可用Bandwidth
```

### 消息界面
```
Calculation of the cost of purchasing energy:

🎯 Address: TQ5kjKLLm9X4L2D1JgogNis6V1YoAm6sv2
ℹ️ Address balance:
TRX: 18.900009
ENERGY: 0
BANDWIDTH: 395

⚡️ Amount: 65 000
📆 Period: 1h 
💵 Cost: 5.85 TRX 

[Buy] [Change address] [Address balance]
```

## 开发环境

### 依赖包
```bash
pip install -r requirements.txt
```

### 配置要求
- **Bot Token**: 在config.py中配置Telegram Bot Token
- **可选API Key**: 环境变量中可配置TRON API Key以获得更高调用限制

### 启动命令
```bash
python main.py
```

## 部署说明

### 生产环境要求
- Python 3.8+
- 稳定的网络连接（访问TRON API）
- Telegram Bot Token（从@BotFather获取）

### 扩展建议
- 使用Redis替代内存状态存储
- 添加数据库持久化钱包地址
- 实现真实的能量租赁交易功能
- 添加TRC-20代币余额查询

## 安全特性

- ✅ 只执行查询操作，不涉及私钥或转账
- ✅ 地址格式验证，防止无效输入
- ✅ 不存储敏感信息，仅缓存余额数据
- ✅ API错误隔离，防止系统崩溃

## 维护指南

### 重要提醒
- 定期检查TRON API连通性
- 监控机器人响应时间和错误率
- 保持Telegram Bot Token的安全性
- 及时更新依赖包版本

### 开发模式
使用环境变量或.env文件管理配置，避免硬编码敏感信息。

这是一个生产就绪的TRON机器人项目，具备完整的钱包管理和余额查询功能。