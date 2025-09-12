# 后端服务部署和测试指南

## 概述

本文档指导如何部署和测试TRON能量助手的后端API服务，包括环境搭建、数据库配置、服务启动和功能验证。

---

## 环境要求

### 系统要求
- **Python**: 3.8 或更高版本
- **PostgreSQL**: 12 或更高版本  
- **Redis**: 6 或更高版本 (可选，用于缓存)
- **Git**: 用于代码管理

### 推荐开发环境
- **Windows**: Python 3.9+ + PostgreSQL 14 + Redis 6
- **Linux/macOS**: 使用包管理器安装上述软件
- **Docker**: 可选，用于容器化部署

---

## 快速部署方案

### 方案一：Docker Compose (推荐)

**优势**: 一键启动所有服务，包含数据库和Redis

```bash
# 进入后端目录
cd backend

# 启动所有服务 (首次启动会自动构建)
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose down
```

**服务地址:**
- API服务: http://localhost:8000
- API文档: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### 方案二：快速启动脚本

**Windows:**
```bash
cd backend
start.bat
```

**Linux/macOS:**
```bash
cd backend
chmod +x start.sh
./start.sh
```

### 方案三：手动部署 (开发调试)

### 1. 代码准备

```bash
# 克隆项目 (如果还没有)
git clone https://github.com/Londonplane/trx-bot.git
cd trx-bot

# 确保在最新版本
git pull origin main
```

### 2. 后端环境搭建

```bash
# 进入后端目录
cd backend

# 创建Python虚拟环境 (推荐)
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖包
pip install -r requirements.txt
```

### 3. 数据库配置

#### 3.1 PostgreSQL安装和配置

**Windows:**
```bash
# 下载并安装PostgreSQL 14+
# https://www.postgresql.org/download/windows/

# 创建数据库
psql -U postgres -c "CREATE DATABASE trx_energy;"
psql -U postgres -c "CREATE USER trx_user WITH PASSWORD 'your_password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE trx_energy TO trx_user;"
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo -u postgres createdb trx_energy
sudo -u postgres createuser --createdb trx_user
sudo -u postgres psql -c "ALTER USER trx_user PASSWORD 'your_password';"
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
createdb trx_energy
createuser --createdb trx_user
psql -c "ALTER USER trx_user PASSWORD 'your_password';"
```

#### 3.2 Redis安装 (可选)

**Windows:**
```bash
# 下载Redis for Windows
# https://github.com/microsoftarchive/redis/releases
# 或使用WSL2安装Linux版本
```

**Ubuntu/Debian:**
```bash
sudo apt install redis-server
sudo systemctl start redis-server
```

**macOS:**
```bash
brew install redis
brew services start redis
```

### 4. 环境变量配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件
nano .env  # 或使用你喜欢的编辑器
```

**`.env` 文件配置示例:**
```bash
# 数据库连接
DATABASE_URL=postgresql://trx_user:your_password@localhost:5432/trx_energy

# Redis连接 (可选)
REDIS_URL=redis://localhost:6379

# JWT密钥 (生产环境必须更改)
SECRET_KEY=your-super-secret-key-change-in-production

# TRON API配置
TRON_API_URL=https://api.trongrid.io
TRON_API_KEY=your-tron-api-key-optional

# 钱包加密密钥 (生产环境必须设置)
WALLET_ENCRYPTION_KEY=your-wallet-encryption-key
```

### 5. 数据库初始化

```bash
# 手动运行SQL创建表结构
python -c "
from app.database import engine, Base
from app.models import *
Base.metadata.create_all(bind=engine)
print('数据库表创建完成')
"

# 或者使用迁移脚本 (如果设置了Alembic)
# alembic upgrade head
```

### 6. 启动后端服务

```bash
# 开发模式启动 (推荐，支持热重载)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 或者直接运行
python main.py

# 成功启动后会看到:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## 功能测试

### 1. 自动化测试脚本

```bash
# 运行完整的API测试套件
cd backend
python test_api.py

# 期望输出:
# 🧪 测试: 健康检查 ✅ 测试通过
# 🧪 测试: 查询用户余额 ✅ 测试通过
# 🧪 测试: 添加钱包地址 ✅ 测试通过
# ...
# 📊 测试结果: 6/6 通过
# 🎉 所有测试通过！后端API服务正常运行
```

### 2. API文档交互测试

启动后端服务后，访问以下地址：

- **API文档**: http://localhost:8000/docs (Swagger UI)
- **备用文档**: http://localhost:8000/redoc (ReDoc)
- **健康检查**: http://localhost:8000/health

### 2. 基础API测试

#### 2.1 健康检查测试
```bash
curl http://localhost:8000/health
# 期望响应: {"status": "healthy", "message": "API服务正常运行"}
```

#### 2.2 用户余额API测试
```bash
# 查询用户余额 (用户ID: 123456)
curl http://localhost:8000/api/users/123456/balance

# 期望响应: {"user_id": 123456, "balance_trx": "0.000000", "balance_usdt": "0.000000"}
```

#### 2.3 钱包管理API测试
```bash
# 添加用户钱包地址
curl -X POST http://localhost:8000/api/wallets/users/123456 \
  -H "Content-Type: application/json" \
  -d '{"wallet_address": "TQ5kjKLLm9X4L2D1JgogNis6V1YoAm6sv2"}'

# 查询用户钱包列表
curl http://localhost:8000/api/wallets/users/123456
```

#### 2.4 订单管理API测试
```bash
# 创建测试订单 (注意：会因余额不足失败，这是正常的)
curl -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123456,
    "energy_amount": 65000,
    "duration": "1h",
    "receive_address": "TQ5kjKLLm9X4L2D1JgogNis6V1YoAm6sv2"
  }'

# 期望响应包含错误信息: "余额不足"
```

### 3. Bot集成测试

#### 3.1 配置Bot连接后端

编辑项目根目录的 `backend_api_client.py`:
```python
# 确保BASE_URL指向正确的后端服务地址
BASE_URL = "http://localhost:8000"  # 本地部署
# BASE_URL = "http://your-server-ip:8000"  # 远程部署
```

#### 3.2 启动Bot测试

```bash
# 在项目根目录启动Bot
cd ..  # 回到项目根目录
python main.py

# 成功启动后Bot会输出:
# Bot正在启动...
# INFO:     Bot启动成功
```

#### 3.3 完整功能测试流程

1. **基础功能测试**:
   - 发送 `/start` → 显示主菜单
   - 点击 "⚡ Buy Energy（闪租）" → 进入闪租页

2. **钱包管理测试**:
   - 点击 "✅ Select address" → 进入钱包管理
   - 点击 "➕ 添加新地址" → 输入TRON地址
   - 验证地址是否保存到数据库

3. **余额查询测试**:
   - 在钱包管理页面查看余额显示
   - 验证余额数据是否来自后端API

4. **订单流程测试**:
   - 选择能量数量和时长
   - 选择接收地址  
   - 点击 "✅ BUY" → 测试订单创建
   - 预期: 显示余额不足消息 (因为是新用户)

#### 3.4 数据验证

```bash
# 检查数据库中的测试数据
docker-compose exec db psql -U trx_user -d trx_energy -c "
SELECT id, balance_trx FROM users WHERE id = 123456;
SELECT user_id, wallet_address FROM user_wallets WHERE user_id = 123456;
SELECT id, user_id, energy_amount, status FROM orders WHERE user_id = 123456;
"
```

---

## 故障排除

### 常见问题

#### 1. 数据库连接失败
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**解决方案:**
- 检查PostgreSQL服务是否启动
- 验证数据库连接字符串是否正确
- 确认数据库用户权限

#### 2. 模块导入错误
```
ModuleNotFoundError: No module named 'app'
```

**解决方案:**
- 确保在backend目录下运行
- 检查Python虚拟环境是否激活
- 验证所有依赖包是否正确安装

#### 3. Bot API调用失败
```
ConnectionError: [Errno 61] Connection refused
```

**解决方案:**
- 确认后端服务已启动并运行在8000端口
- 检查`backend_api_client.py`中的`base_url`配置
- 验证防火墙没有阻塞8000端口

#### 4. TRON API调用异常
```
requests.exceptions.RequestException
```

**解决方案:**
- 检查网络连接
- 验证TRON API节点是否可用
- 检查API Key配置 (如果使用)

### 调试技巧

#### 1. 启用详细日志
```python
# 在main.py中添加
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 2. 数据库查询验证
```bash
# 连接数据库检查数据
psql -d trx_energy -c "SELECT * FROM users;"
psql -d trx_energy -c "SELECT * FROM orders;"
psql -d trx_energy -c "SELECT * FROM user_wallets;"
```

#### 3. API响应调试
使用Postman或curl测试API接口，检查响应状态码和数据格式。

---

## 性能验证

### 1. API响应时间
```bash
# 测试API响应时间
time curl http://localhost:8000/api/users/123456/balance
```

### 2. 并发测试
```bash
# 简单并发测试 (需要安装ab)
ab -n 100 -c 10 http://localhost:8000/health
```

### 3. 数据库性能
```sql
-- 检查数据库查询性能
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 123456;
```

---

## 生产环境考虑

### 1. 环境变量安全
- 生产环境必须使用强密码和密钥
- 使用环境变量管理敏感信息
- 定期轮换密钥和密码

### 2. 数据库优化
- 设置合适的连接池大小
- 添加必要的数据库索引
- 定期备份数据库

### 3. 监控和日志
- 配置结构化日志输出
- 设置API响应时间监控
- 添加错误率报警

### 4. 安全加固
- 配置HTTPS/SSL
- 设置API访问限流
- 添加请求认证机制

---

## 下一步开发

完成基础后端服务部署测试后，可以继续开发：

1. **TRON交易引擎**: 实现真实的Energy委托交易
2. **充值监控系统**: 自动监控和确认用户充值
3. **供应商钱包池**: 管理多个钱包和Energy库存
4. **管理员界面**: Web管理后台开发

参考文档: `docs/闪租页后端开发计划.md`

---

## 部署总结

### 🚀 最快启动方式 (推荐新手)

```bash
# 1. 克隆项目
git clone https://github.com/Londonplane/trx-bot.git
cd trx-bot/backend

# 2. Docker一键启动
docker-compose up -d

# 3. 等待服务启动 (约30-60秒)
docker-compose logs -f backend

# 4. 运行API测试
python test_api.py

# 5. 启动Bot测试集成
cd ..
python main.py
```

### ✅ 成功验证清单

- [ ] 后端服务启动成功 (http://localhost:8000/health 返回正常)
- [ ] API文档可访问 (http://localhost:8000/docs 显示接口文档)
- [ ] 数据库连接正常 (test_api.py 全部测试通过)
- [ ] Bot可以启动并连接后端 (Bot日志无API连接错误)
- [ ] 钱包地址可以添加并保存到数据库
- [ ] 订单API调用正常 (即使余额不足也应返回明确错误)

### 📋 常用维护命令

```bash
# 查看服务状态
docker-compose ps

# 重启后端服务
docker-compose restart backend

# 查看数据库数据
docker-compose exec db psql -U trx_user -d trx_energy -c "SELECT COUNT(*) FROM users;"

# 备份数据库
docker-compose exec db pg_dump -U trx_user trx_energy > backup.sql

# 清理并重新启动
docker-compose down -v  # 删除数据卷
docker-compose up -d    # 重新启动
```

### 🔧 开发模式

如果需要修改代码并实时测试：

```bash
# 停止Docker中的backend服务
docker-compose stop backend

# 手动启动后端 (支持热重载)
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 数据库和Redis继续使用Docker
# 这样可以边改代码边测试
```

---

## 下一步开发

完成基础后端服务部署测试后，可以继续开发：

1. **TRON交易引擎**: 实现真实的Energy委托交易
2. **充值监控系统**: 自动监控和确认用户充值
3. **供应商钱包池**: 管理多个钱包和Energy库存
4. **管理员界面**: Web管理后台开发

参考文档: `docs/闪租页后端开发计划.md`

---

*最后更新: 2025-08-23*
*适用版本: v2.1 - 闪租页后端集成版本*