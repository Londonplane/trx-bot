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
├── launcher.py              # 🆕 生产级启动器（推荐使用）
├── encoding_fix.py          # 🆕 Windows编码修复模块
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
│   └── docker-compose.yml # 容器化部署配置
├── docs/                  # 完整的项目文档
└── 启动器使用指南.md        # 🆕 详细使用说明
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

#### 🆕 推荐方式：生产级启动器
```bash
# 安装依赖（仅首次运行）
pip install -r requirements.txt
pip install -r backend/requirements.txt

# 一键启动所有服务
python launcher.py
```

**特性**：
- ✅ 自动启动后端API和Telegram Bot
- ✅ 实时健康监控和自动重启
- ✅ 完美解决Windows编码问题
- ✅ 优雅的进程管理和关闭

**验证**: 启动后访问 http://localhost:8002/health 应返回健康状态

#### 传统方式：手动启动
```bash
# 1. 启动后端服务
cd backend && python main.py &

# 2. 启动Telegram Bot（新终端）
python main.py
```

⚠️ **注意**: 传统方式可能遇到编码问题，建议使用生产级启动器

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
- **端口**: 确保8002端口可用（后端API服务）
- **域名**: 可选，用于Webhook模式
- **SSL证书**: 如使用Webhook模式需要

### 部署方式

#### 🆕 推荐方案：生产级启动器
```bash
# 生产环境部署
python launcher.py
```

**优势**：
- 自动故障检测和重启（最多3次）
- 完整的服务健康监控
- 优雅的进程生命周期管理
- 无编码问题，跨平台兼容

#### 传统方案：手动部署
```bash
# 方案一：直接启动
cd backend && python main.py &
cd .. && python main.py

# 方案二：进程管理器
pm2 start launcher.py --name "tron-energy-bot"
```

#### Docker部署
```bash
# 使用后端目录中的docker-compose.yml
cd backend
docker-compose up -d
```

### 故障恢复机制
- **自动重启**: 生产级启动器内置故障检测和自动重启
- **后端API失败**: Bot自动使用本地文件存储和Mock数据
- **区块链API失败**: 自动切换备用API端点
- **会话恢复**: 重启后自动加载用户钱包地址

## 安全特性

- ✅ 只执行查询操作，不涉及私钥或转账
- ✅ 地址格式验证，防止无效输入
- ✅ 不存储敏感信息，仅缓存余额数据
- ✅ API错误隔离，防止系统崩溃

## 故障排除

### 🆕 推荐解决方案
**使用生产级启动器可以避免99%的常见问题！**

```bash
# 一键解决所有启动问题
python launcher.py
```

### 常见问题

#### 1. 编码错误 (UnicodeEncodeError/GBK)
**症状**: `'gbk' codec can't encode/decode character`
**解决**: 使用生产级启动器，已完美解决编码问题
```bash
python launcher.py  # 自动处理所有编码问题
```

#### 2. 服务意外停止
**症状**: Backend或Bot进程意外退出
**解决**: 生产级启动器自动重启（最多3次）
- 自动检测服务状态
- 智能故障恢复
- 详细的错误报告

#### 3. 连接被拒绝错误 (WinError 10061)
**症状**: `HTTPConnectionPool(host='localhost', port=8002): Max retries exceeded`
**原因**: 后端API服务未启动
**解决**: 
```bash
# 生产级启动器会自动处理
python launcher.py
```

#### 4. Bot Token配置错误
**解决**:
- 检查config.py中的BOT_TOKEN配置
- 或设置环境变量: `TELEGRAM_BOT_TOKEN`

### 监控与日志
- **实时状态**: 生产级启动器显示所有服务状态
- **健康检查**: http://localhost:8002/health
- **API文档**: http://localhost:8002/docs
- **服务监控**: 自动检测和重启失败的服务

### 维护建议
- **推荐启动方式**: 始终使用 `python launcher.py`
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