# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个功能完整的TRON能量助手Telegram机器人项目，采用前后端分离的架构设计。机器人实现了钱包管理、余额查询和能量租赁功能，用户可以通过Telegram界面管理TRON钱包地址并查询实时余额信息。

## 核心功能

### 已实现功能
- **钱包管理系统**: 用户可以添加、删除和选择多个TRON钱包地址
- **实时余额查询**: 查询TRX余额、Energy余额和Bandwidth余额
- **闪租页面**: 能量租赁界面，支持参数选择和地址管理
- **地址验证**: 自动验证TRON地址格式
- **双API支持**: 使用TronScan API作为主要接口，官方TRON API作为备用
- **后端API集成**: 完整的用户余额、订单管理、钱包地址存储系统
- **容错机制**: API失败时自动切换到本地存储和Mock数据

### 技术特色
- **前后端分离**: Telegram Bot + FastAPI后端服务架构
- **智能地址管理**: 用户绑定的地址列表，支持数据库和本地文件双重存储
- **实时API集成**: 真实的TRON区块链数据查询
- **无缝用户体验**: 所有操作通过消息编辑完成，保持上下文
- **完善错误处理**: 网络异常、地址验证、API失败等场景的优雅处理
- **高可用性**: 后端不可用时仍能提供基本功能

## 项目架构

### 核心文件结构
```
trx-bot/
├── main.py                  # Telegram Bot主程序入口
├── buy_energy.py            # 闪租页面逻辑和余额查询
├── models.py                # 数据模型和用户会话管理（含容错机制）
├── tron_api.py             # TRON区块链API客户端
├── backend_api_client.py    # 后端API客户端封装
├── config.py               # 配置文件（Bot Token等）
├── requirements.txt        # Bot依赖包
├── user_wallets.json       # 本地钱包地址备份文件
├── backend/                # 后端API服务
│   ├── main.py            # FastAPI服务入口
│   ├── app/               # API应用代码
│   ├── requirements.txt   # 后端依赖包
│   ├── docker-compose.yml # 容器化部署配置
│   └── start_services.bat # Windows启动脚本
└── docs/                  # 完整的项目文档
```

### 系统架构设计
- **Telegram Bot层**: 用户界面交互，会话状态管理
- **后端API层**: 用户数据持久化，订单处理，余额管理
- **区块链API层**: TRON网络数据查询，余额验证
- **容错机制层**: API失败时的备用数据源和降级服务

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

### 系统要求
- **Python**: 3.8+ 
- **操作系统**: Windows 10/11, macOS, Linux
- **内存**: 建议8GB+
- **网络**: 稳定的网络连接（访问TRON API和Telegram API）

### 快速启动

#### 1. 启动后端服务（必需）
```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务（Windows）
start_services.bat

# 或手动启动（跨平台）
python main.py
```
**验证**: 访问 http://localhost:8001/health 应返回 `{"status":"healthy"}`

#### 2. 启动Telegram Bot
```bash
# 在项目根目录
pip install -r requirements.txt

# 配置Bot Token到config.py
# 启动Bot
python main.py
```

### 依赖包管理
- **Bot依赖**: requirements.txt（含python-telegram-bot等）
- **后端依赖**: backend/requirements.txt（含FastAPI、SQLAlchemy等）

### 配置要求
- **必需**: Telegram Bot Token（在config.py中配置）
- **可选**: TRON API Key（环境变量，用于更高的调用限制）
- **数据库**: 默认使用SQLite，生产环境可配置PostgreSQL

## 部署说明

### 生产环境要求
- **服务器**: VPS或云服务器，推荐2GB+ 内存
- **端口**: 确保8001端口可用（后端API服务）
- **域名**: 可选，用于Webhook模式
- **SSL证书**: 如使用Webhook模式需要

### 部署方式

#### 方案一：直接部署
```bash
# 1. 启动后端服务
cd backend && python main.py &

# 2. 启动Bot
cd .. && python main.py
```

#### 方案二：Docker部署
```bash
# 使用后端目录中的docker-compose.yml
cd backend
docker-compose up -d
```

#### 方案三：进程管理器
```bash
# 使用PM2、Supervisor等进程管理器
pm2 start backend/main.py --name "trx-backend"
pm2 start main.py --name "trx-bot"
```

### 故障恢复机制
- **后端API失败**: Bot自动使用本地文件存储和Mock数据
- **区块链API失败**: 自动切换备用API端点
- **会话恢复**: 重启后自动加载用户钱包地址

## 安全特性

- ✅ 只执行查询操作，不涉及私钥或转账
- ✅ 地址格式验证，防止无效输入
- ✅ 不存储敏感信息，仅缓存余额数据
- ✅ API错误隔离，防止系统崩溃

## 故障排除

### 常见问题

#### 1. 连接被拒绝错误 (WinError 10061)
**症状**: `HTTPConnectionPool(host='localhost', port=8001): Max retries exceeded`
**原因**: 后端API服务未启动
**解决**:
```bash
# 确保后端服务运行
cd backend && python main.py
# 验证服务: curl http://localhost:8001/health
```

#### 2. Bot无响应或功能异常
**可能原因**: Bot Token配置错误、网络问题
**解决**:
- 检查config.py中的BOT_TOKEN配置
- 验证网络连接和防火墙设置
- 查看终端日志输出

#### 3. 余额查询失败
**症状**: 显示Mock数据或查询失败
**解决**:
- 检查后端服务状态
- 验证TRON API网络连接
- 查看日志中的API调用错误

### 监控与日志
- **Bot日志**: 终端输出包含详细的操作日志
- **后端日志**: FastAPI服务的访问和错误日志
- **健康检查**: http://localhost:8001/health
- **API文档**: http://localhost:8001/docs

### 维护建议
- **定期检查**: 监控API服务状态和响应时间
- **数据备份**: 定期备份user_wallets.json和数据库文件
- **更新依赖**: 及时更新Python包版本
- **安全检查**: 保护Bot Token和API密钥安全

## 项目特色

这是一个**生产就绪**的TRON机器人项目，具备以下特色：

### 🏗️ 架构优势
- **前后端分离**: 模块化设计，易于扩展和维护
- **高可用性**: 多层容错机制，服务失败时自动降级
- **数据持久化**: 数据库存储+本地文件备份双重保障

### 🚀 技术优势
- **实时查询**: 真实TRON区块链数据，非模拟数据
- **智能缓存**: 会话状态管理，提升用户体验
- **API集成**: 完整的RESTful API，支持扩展开发

### 💡 用户体验
- **零配置**: 地址管理全自动，用户无需手动配置
- **即时响应**: 消息编辑实时更新，保持上下文连续
- **容错友好**: 网络异常时仍能正常使用基本功能

### 📈 扩展潜力
- **订单系统**: 完整的能量租赁下单流程框架
- **用户管理**: 支持用户余额、充值、消费记录
- **监控系统**: 内置健康检查和日志监控能力

这个项目不仅解决了基本的TRON钱包查询需求，更提供了一个完整的、可扩展的Telegram Bot开发框架。