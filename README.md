# TRON能量助手项目

一个功能完整的TRON能量供应商Telegram机器人及后台管理系统。

## 项目概述

- **前端**: Telegram Bot - 用户通过Telegram界面管理钱包和购买能量
- **后端**: FastAPI服务 - 处理订单、管理钱包池、执行TRON交易
- **数据库**: PostgreSQL/SQLite - 存储用户、订单、钱包等业务数据
- **任务队列**: Celery + Redis - 异步处理交易和监控任务

## 核心功能

### Telegram Bot (已完成)
- ✅ 钱包地址管理 (添加/删除/选择)
- ✅ 实时TRON余额查询 (TRX/Energy/Bandwidth)
- ✅ 闪租页面 (能量数量和时长选择)
- ✅ 地址验证和错误处理
- ✅ 双API容错机制 (TronScan + 官方API)
- ✅ 后端API集成 (真实余额和订单管理)

### 后端管理系统 (已完成)
- ✅ **订单管理API** - 完整的能量租赁订单生命周期
- ✅ **用户余额系统** - 真实的TRX/USDT余额管理和充值确认
- ✅ **供应商钱包池** - 多钱包管理、私钥加密存储、智能选择
- ✅ **TRON交易引擎** - 自动化能量委托交易执行
- ✅ **后台任务系统** - 定时处理订单、更新余额、监控异常
- 🔄 **监控报警系统** - 7x24小时运营监控 (计划中)
- 🔄 **管理员界面** - Web管理后台 (计划中)

### 🎯 新增核心特性

#### TRON交易引擎
- **智能钱包选择**: 根据能量需求自动选择最优供应商钱包
- **加密安全存储**: 基于Fernet算法的私钥加密存储机制
- **自动化交易流程**: pending → processing → completed/failed
- **容错和重试**: 交易失败自动重试和退款机制

#### 后台任务系统
- **异步订单处理**: 订单创建后立即触发后台处理
- **定时任务调度**: 30秒处理订单，5分钟更新钱包余额
- **任务队列分离**: orders队列和wallets队列独立管理

## 技术架构

### Bot端
- **Python 3.8+** + python-telegram-bot
- **TronScan API** + 官方TRON API
- **后端API集成** - 真实数据替代Mock数据

### 后端服务
- **FastAPI** - 高性能异步Web框架
- **PostgreSQL/SQLite** - 主数据库，支持本地和生产环境
- **Redis** - 缓存和任务队列 (可选)
- **Celery** - 异步任务处理
- **tronpy** - TRON区块链交互库

## 快速开始

### 🏠 本地测试 (推荐首次使用)

```bash
# 1. 启动后端服务
cd backend && start_services.bat  # Windows
cd backend && ./start_services.sh # Linux/macOS

# 2. 验证API服务
curl http://localhost:8001/health

# 3. 启动Telegram Bot
python main.py
```

**本地测试指南**: [docs/本地测试指南.md](docs/本地测试指南.md) - 30分钟完成功能验证

### 🚀 生产环境部署

详细部署指南: [docs/正式场景测试指南.md](docs/正式场景测试指南.md)

快速清单: [docs/生产测试快速清单.md](docs/生产测试快速清单.md)

## API接口

### 用户管理
- `GET /api/users/{user_id}/balance` - 查询用户余额
- `POST /api/users/{user_id}/deposit` - 确认用户充值
- `GET /api/users/{user_id}/transactions` - 查询余额变动记录

### 订单管理
- `POST /api/orders/` - 创建能量租赁订单
- `GET /api/orders/{order_id}` - 查询订单详情
- `GET /api/orders?user_id={id}` - 查询用户订单列表
- `POST /api/orders/{order_id}/cancel` - 取消订单

### 供应商钱包管理
- `GET /api/supplier-wallets/` - 查看钱包池
- `POST /api/supplier-wallets/add` - 添加供应商钱包
- `POST /api/supplier-wallets/update-balances` - 更新钱包余额
- `POST /api/supplier-wallets/process-orders` - 手动处理订单

## 项目结构

```
trx-bot/
├── main.py                        # Telegram Bot主程序
├── buy_energy.py                 # 闪租页面业务逻辑  
├── models.py                     # 数据模型和会话管理
├── tron_api.py                   # TRON API客户端
├── backend_api_client.py         # 后端API客户端
├── config.py                     # Bot配置文件
├── requirements.txt              # Bot依赖包
├── backend/                      # 后端API服务
│   ├── main.py                  # FastAPI应用入口
│   ├── tron_worker.py           # Celery异步任务处理
│   ├── start_services.bat/.sh   # 自动启动脚本
│   ├── app/                     # 应用核心代码
│   │   ├── api/                # API路由
│   │   │   ├── orders.py       # 订单管理API
│   │   │   ├── users.py        # 用户管理API
│   │   │   ├── wallets.py      # 钱包管理API
│   │   │   └── supplier_wallets.py # 供应商钱包API
│   │   ├── models/             # 数据库模型
│   │   ├── services/           # 业务逻辑
│   │   │   ├── order_service.py     # 订单服务
│   │   │   ├── user_service.py      # 用户服务
│   │   │   ├── wallet_service.py    # 钱包服务
│   │   │   └── tron_service.py      # TRON交易服务
│   │   ├── database.py         # 数据库配置
│   │   └── schemas.py          # 数据验证模型
│   └── requirements.txt        # 后端依赖包
├── docs/                        # 项目文档
│   ├── 开发日志.md              # 详细开发记录
│   ├── TRON交易引擎部署测试指南.md # 部署指南
│   └── ...                     # 其他技术文档
└── tests/                       # 测试代码
```

## 开发进度

- [x] **阶段1**: Telegram Bot基础功能完成 ✅
- [x] **阶段2**: 后台管理系统设计完成 ✅
- [x] **阶段3**: 后端API开发完成 ✅
- [x] **阶段4**: TRON交易引擎开发完成 ✅
- [ ] **阶段5**: 监控和管理界面 (计划中)
- [ ] **阶段6**: 生产部署优化 (计划中)

### 当前版本: v2.2 - TRON交易引擎集成

**✅ 已完成功能:**
- 完整的TRON交易引擎和供应商钱包池管理
- 15个API端点全部开发完成并测试通过
- 企业级安全机制和私钥加密存储
- 自动化部署脚本和完整文档
- 生产就绪的架构和配置

详细开发记录见: [docs/开发日志.md](docs/开发日志.md)

## 安全特性

- ✅ Bot端只执行查询操作，不涉及私钥存储
- ✅ 地址格式验证，防止无效输入
- ✅ API错误隔离和容错处理
- ✅ 供应商钱包私钥Fernet加密存储
- ✅ 完整的异常处理和自动退款机制
- ✅ 交易重试和状态监控
- 🔄 API认证授权机制 (开发中)
- 🔄 请求限流和安全审计 (计划中)

## 部署指南

### 生产环境部署

1. **环境准备**
   - Python 3.8+
   - PostgreSQL 12+ (或SQLite用于测试)
   - Redis 6+ (可选，用于Celery)
   - TRON网络访问权限

2. **配置环境变量**
   ```bash
   DATABASE_URL=postgresql://user:password@localhost:5432/trx_energy
   REDIS_URL=redis://localhost:6379
   SECRET_KEY=your-production-secret-key
   ENCRYPTION_KEY=your-fernet-encryption-key
   TRON_API_KEY=your-tron-api-key
   ```

3. **启动服务**
   ```bash
   # 使用自动化脚本
   cd backend && ./start_services.sh
   ```

详细部署指南: [docs/TRON交易引擎部署测试指南.md](docs/TRON交易引擎部署测试指南.md)

## 测试验证

### API测试示例
```bash
# 健康检查
curl http://localhost:8001/health

# 用户充值
curl -X POST http://localhost:8001/api/users/123456/deposit \
  -H "Content-Type: application/json" \
  -d '{"tx_hash": "0x...64chars", "amount": 10.0, "currency": "TRX"}'

# 创建订单
curl -X POST http://localhost:8001/api/orders/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": 123456, "energy_amount": 65000, "duration": "1h", "receive_address": "TR..."}'
```

## 监控和维护

- 📊 **日志系统**: 完整的操作日志和错误追踪
- 📈 **性能监控**: API响应时间和数据库查询性能
- 🔄 **自动化任务**: 定时订单处理和钱包余额更新
- ⚠️ **异常处理**: 自动重试、退款和错误恢复

## 联系方式

- **GitHub Issues**: 提交bug报告和功能请求
- **技术文档**: 查看 `docs/` 目录获取详细文档
- **开发日志**: `docs/开发日志.md` 记录了完整的开发过程

---

**当前版本**: v2.2 - TRON交易引擎集成完成  
**最后更新**: 2025-08-24  
**项目状态**: 🎯 生产就绪