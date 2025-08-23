# TRON能量助手后端服务

## 快速启动指南

### 1. 环境准备

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，设置数据库连接等配置
```

### 2. 数据库设置

```bash
# 创建PostgreSQL数据库
createdb trx_energy

# 运行数据库迁移
alembic upgrade head
```

### 3. 启动服务

```bash
# 开发模式启动
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 或者直接运行
python main.py
```

### 4. API文档
启动后访问: http://localhost:8000/docs

## 服务架构

### 核心组件
- **FastAPI**: Web API框架
- **SQLAlchemy**: ORM数据库操作
- **PostgreSQL**: 主数据库
- **Redis**: 缓存和会话存储

### API端点
- `/api/orders` - 订单管理
- `/api/users` - 用户余额管理  
- `/api/wallets` - 钱包地址管理

### 与Bot集成
Bot通过 `backend_api_client.py` 调用后端API，实现：
- 真实用户余额查询和管理
- 订单创建和状态跟踪
- 钱包地址持久化存储

## 开发状态
- ✅ 基础API框架
- ✅ 数据库模型设计
- ✅ 核心业务逻辑
- 🔄 TRON交易引擎（开发中）
- ⏳ 管理员界面（待开发）