# 后台管理系统技术栈选择

## 核心技术栈

### 1. 后端API服务
**选择：FastAPI + Python 3.8+**

**理由：**
- 与现有Telegram Bot（Python）技术栈一致
- 高性能异步框架，适合处理大量并发订单
- 自动生成OpenAPI文档，便于前端集成
- 内置数据验证和序列化
- 优秀的WebSocket支持（实时监控需要）

**替代方案：**
- Flask + Flask-RESTful（更轻量，但需要更多手动配置）

### 2. 数据库
**选择：PostgreSQL 13+**

**理由：**
- 支持JSON字段存储配置和元数据
- 优秀的事务支持（订单处理关键）
- 支持复杂查询和聚合（财务报表）
- 高并发性能
- 丰富的索引类型

**数据库连接：**
- SQLAlchemy ORM + Alembic迁移
- asyncpg异步驱动（配合FastAPI）

### 3. 缓存和队列
**选择：Redis 6+**

**用途：**
- 用户会话状态缓存（替代内存存储）
- 钱包余额缓存（减少TRON API调用）
- 订单处理队列
- 分布式锁（防止并发问题）

### 4. 任务队列
**选择：Celery + Redis**

**用途：**
- 异步处理能量委托交易
- 定时任务（余额监控、订单超时清理）
- 充值确认任务
- 报表生成任务

### 5. 区块链集成
**选择：tronpy + 现有tron_api.py**

**扩展功能：**
- 私钥管理和交易签名
- Energy委托合约调用
- 交易状态监控
- 批量交易处理

## 项目结构设计

```
trx-energy-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口
│   ├── database.py          # 数据库连接配置
│   ├── models/             # SQLAlchemy模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── order.py
│   │   ├── wallet.py
│   │   └── config.py
│   ├── api/                # API路由
│   │   ├── __init__.py
│   │   ├── orders.py
│   │   ├── users.py
│   │   ├── wallets.py
│   │   └── admin.py
│   ├── services/           # 业务逻辑
│   │   ├── __init__.py
│   │   ├── order_service.py
│   │   ├── wallet_service.py
│   │   ├── payment_service.py
│   │   └── monitor_service.py
│   ├── tasks/              # Celery任务
│   │   ├── __init__.py
│   │   ├── order_tasks.py
│   │   ├── wallet_tasks.py
│   │   └── monitor_tasks.py
│   └── utils/              # 工具函数
│       ├── __init__.py
│       ├── tron_client.py  # 扩展版tron_api
│       ├── crypto.py       # 加密工具
│       └── validators.py
├── migrations/             # Alembic数据库迁移
├── tests/                  # 测试代码
├── docker-compose.yml      # 容器编排
├── Dockerfile
├── requirements.txt
└── .env.example
```

## 现有Bot集成方案

### 方式1：共享数据库模式
```
Telegram Bot (现有) ←→ PostgreSQL ←→ Backend API
                    ↓
                   Redis缓存
```

### 方式2：API调用模式
```
Telegram Bot → Backend API → PostgreSQL
                          ↓
                         Redis
```

**推荐方式2**，将现有Bot改造为Backend API的客户端：

1. 修改`models.py`：替换JSON文件存储为API调用
2. 修改`buy_energy.py`：订单创建调用Backend API
3. 添加用户余额API调用，替换Mock数据

## 部署架构

### 开发环境
```yaml
# docker-compose.dev.yml
services:
  backend:
    build: .
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/trx_energy
      - REDIS_URL=redis://redis:6379
  
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: trx_energy
  
  redis:
    image: redis:6-alpine
  
  celery:
    build: .
    command: celery -A app.tasks worker --loglevel=info
```

### 生产环境
- Nginx反向代理
- SSL/TLS证书
- 数据库主从复制
- Redis集群
- 容器监控（Prometheus + Grafana）

## 安全考虑

### 私钥管理
- 使用AES-256加密存储私钥
- 密钥分离存储（环境变量）
- 定期密钥轮换

### API安全
- JWT token认证
- 请求限流
- IP白名单
- 敏感操作审计日志

### 数据安全
- 数据库连接SSL
- 定期数据备份
- 敏感数据脱敏

## 监控方案

### 应用监控
- FastAPI内置metrics
- 自定义业务指标
- 错误日志聚合

### 基础设施监控
- 数据库性能监控
- Redis内存使用
- 容器资源监控

### 业务监控
- 订单成功率
- 钱包余额预警
- API响应时间