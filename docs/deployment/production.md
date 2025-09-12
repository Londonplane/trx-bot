# TRON交易引擎部署和测试指南

## 概述

本指南详细说明了TRON能量助手的交易引擎部署、配置和测试流程。交易引擎包括供应商钱包管理、能量委托交易、后台任务处理等核心功能。

## 系统架构

### 核心组件

1. **FastAPI后端服务** (端口8001)
   - RESTful API接口
   - 用户余额管理
   - 订单生命周期管理
   - 供应商钱包池管理

2. **TRON交易服务** (TronTransactionService)
   - 私钥加密存储
   - 区块链交易执行
   - 钱包余额监控
   - 智能钱包选择

3. **后台任务系统** (Celery + Redis)
   - 异步订单处理
   - 定时余额更新
   - 任务队列管理

4. **数据库层** (SQLite/PostgreSQL)
   - 用户数据持久化
   - 订单状态管理
   - 钱包信息存储

## 快速部署

### 环境要求

- Python 3.8+
- Docker (可选，用于PostgreSQL和Redis)
- TRON网络访问权限

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 环境变量配置

创建 `.env` 文件：

```bash
# 数据库配置
DATABASE_URL=sqlite:///./trx_energy.db
# 或使用PostgreSQL：DATABASE_URL=postgresql://user:password@localhost:5432/trx_energy

# Redis配置（可选，用于Celery）
REDIS_URL=redis://localhost:6379

# 安全密钥
SECRET_KEY=your-super-secret-key-change-in-production

# TRON网络配置
TRON_NETWORK=mainnet  # mainnet | testnet
TRON_API_KEY=your-tron-api-key-optional

# 加密密钥（用于私钥加密）
ENCRYPTION_KEY=your-encryption-key-32-bytes-base64-encoded
```

### 3. 启动服务

#### Windows
```cmd
start_services.bat
```

#### Linux/MacOS
```bash
chmod +x start_services.sh
./start_services.sh
```

#### 手动启动
```bash
# 启动API服务
python main.py

# 启动Celery Worker（如果有Redis）
celery -A tron_worker worker --loglevel=info

# 启动Celery Beat（定时任务）
celery -A tron_worker beat --loglevel=info
```

## API接口测试

### 基础健康检查

```bash
# 检查服务状态
curl -X GET http://localhost:8001/health
# 响应：{"status":"healthy","message":"API服务正常运行"}

# 检查API版本
curl -X GET http://localhost:8001/
# 响应：{"message":"TRON Energy Backend API","version":"1.0.0"}
```

### 用户余额管理测试

```bash
# 1. 查询用户余额
curl -X GET http://localhost:8001/api/users/123456/balance

# 2. 用户充值（模拟）
curl -X POST http://localhost:8001/api/users/123456/deposit \
  -H "Content-Type: application/json" \
  -d '{
    "tx_hash": "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
    "amount": 10.0,
    "currency": "TRX"
  }'

# 3. 查询余额变动记录
curl -X GET http://localhost:8001/api/users/123456/transactions
```

### 订单管理测试

```bash
# 1. 创建订单
curl -X POST http://localhost:8001/api/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123456,
    "energy_amount": 65000,
    "duration": "1h",
    "receive_address": "TQ5kjKLLm9X4L2D1JgogNis6V1YoAm6sv2"
  }'

# 2. 查询订单详情
curl -X GET http://localhost:8001/api/orders/{order_id}

# 3. 查询用户订单列表
curl -X GET http://localhost:8001/api/orders?user_id=123456&limit=10

# 4. 取消订单
curl -X POST http://localhost:8001/api/orders/{order_id}/cancel
```

### 供应商钱包管理测试

```bash
# 1. 查看钱包池
curl -X GET http://localhost:8001/api/supplier-wallets/

# 2. 添加供应商钱包（需要真实私钥）
curl -X POST http://localhost:8001/api/supplier-wallets/add \
  -H "Content-Type: application/json" \
  -d '{
    "private_key": "your-supplier-wallet-private-key"
  }'

# 3. 更新钱包余额
curl -X POST http://localhost:8001/api/supplier-wallets/update-balances

# 4. 手动处理订单
curl -X POST http://localhost:8001/api/supplier-wallets/process-orders

# 5. 启用/禁用钱包
curl -X PUT http://localhost:8001/api/supplier-wallets/{wallet_id}/toggle
```

## 完整业务流程测试

### 端到端测试场景

1. **用户充值流程**
   ```bash
   # 模拟用户充值10 TRX
   curl -X POST http://localhost:8001/api/users/999888/deposit \
     -H "Content-Type: application/json" \
     -d '{
       "tx_hash": "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
       "amount": 10.0,
       "currency": "TRX"
     }'
   ```

2. **创建能量租赁订单**
   ```bash
   # 租赁65,000能量，1小时
   curl -X POST http://localhost:8001/api/orders/ \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": 999888,
       "energy_amount": 65000,
       "duration": "1h",
       "receive_address": "TTestAddress1234567890123456789012"
     }'
   ```

3. **监控订单处理**
   ```bash
   # 查询订单状态变化：pending → processing → completed
   curl -X GET http://localhost:8001/api/orders/{order_id}
   ```

4. **验证余额扣减**
   ```bash
   # 确认用户余额被正确扣减
   curl -X GET http://localhost:8001/api/users/999888/balance
   ```

## 监控和日志

### 应用日志

日志记录了所有关键操作：

- 订单创建和状态变化
- TRON网络交互
- 钱包余额更新
- 错误和异常处理

```bash
# 查看实时日志（如果使用systemd）
journalctl -f -u tron-backend

# 查看应用日志文件
tail -f /var/log/tron-backend.log
```

### 性能监控

```bash
# API响应时间测试
time curl -X GET http://localhost:8001/api/users/123456/balance

# 数据库查询性能
sqlite3 trx_energy.db "EXPLAIN QUERY PLAN SELECT * FROM orders WHERE user_id = 123456;"
```

## 故障排查

### 常见问题

1. **TRON网络连接失败**
   - 检查网络连接
   - 验证API密钥配置
   - 确认TRON节点可访问性

2. **私钥解密失败**
   - 检查ENCRYPTION_KEY环境变量
   - 验证私钥格式（64字符十六进制）

3. **Celery任务不执行**
   - 检查Redis连接
   - 确认Celery Worker运行状态
   - 查看任务队列状态

4. **数据库连接问题**
   - 检查DATABASE_URL配置
   - 验证数据库权限
   - 确认表结构已创建

### 诊断命令

```bash
# 检查数据库连接
python -c "from app.database import engine; print(engine.execute('SELECT 1').scalar())"

# 检查Redis连接
python -c "import redis; r=redis.from_url('redis://localhost:6379'); print(r.ping())"

# 检查TRON网络连接
python -c "from tronpy import Tron; t=Tron(); print(t.get_latest_block_number())"

# 检查Celery状态
celery -A tron_worker status

# 查看活跃任务
celery -A tron_worker active
```

## 生产环境配置

### 安全配置

1. **环境变量管理**
   - 使用强随机密钥
   - 定期轮换加密密钥
   - 限制私钥访问权限

2. **网络安全**
   - 配置防火墙规则
   - 使用HTTPS/TLS
   - 限制API访问来源

3. **数据库安全**
   - 使用专用数据库用户
   - 启用连接加密
   - 定期备份数据

### 性能优化

1. **数据库优化**
   ```sql
   -- 创建必要索引
   CREATE INDEX idx_orders_user_id ON orders(user_id);
   CREATE INDEX idx_orders_status ON orders(status);
   CREATE INDEX idx_balance_transactions_user_id ON balance_transactions(user_id);
   ```

2. **缓存配置**
   - 启用Redis缓存
   - 配置适当的TTL
   - 实现查询结果缓存

3. **并发配置**
   - 调整Celery Worker数量
   - 配置数据库连接池
   - 优化API并发处理

## 版本升级指南

### 升级步骤

1. **备份数据**
   ```bash
   # 备份SQLite数据库
   cp trx_energy.db trx_energy.db.backup
   
   # 或导出PostgreSQL
   pg_dump trx_energy > backup_$(date +%Y%m%d).sql
   ```

2. **更新代码**
   ```bash
   git pull origin main
   pip install -r requirements.txt
   ```

3. **执行迁移**
   ```bash
   # 如果有数据库结构变更
   python migrations/run_migrations.py
   ```

4. **重启服务**
   ```bash
   ./start_services.sh
   ```

## 支持和维护

### 定期维护任务

1. **日志轮转和清理**
2. **数据库性能分析**
3. **监控指标检查**
4. **安全更新应用**

### 联系支持

- GitHub Issues: https://github.com/your-project/issues
- 技术文档: ./docs/
- 开发日志: ./docs/开发日志.md

---

**最后更新**: 2025-08-24
**版本**: v2.2 - TRON交易引擎集成
**作者**: TRON能量助手开发团队