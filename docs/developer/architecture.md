# 技术架构设计

## 🏗️ 系统架构概述

TRON能量助手采用前后端分离的微服务架构，包含Telegram Bot前端、FastAPI后端服务、数据库存储和TRON区块链集成。

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Telegram      │    │   FastAPI        │    │   PostgreSQL    │
│   Bot Frontend  │◄──►│   Backend API    │◄──►│   Database      │
│   (main.py)     │    │   (backend/)     │    │   (Optional)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        
         │              ┌──────────────────┐               
         └──────────────►│   TRON Network   │               
                        │   APIs           │               
                        └──────────────────┘               
```

## 🎯 核心设计原则

### 1. 分层架构
- **表示层**: Telegram Bot用户界面
- **业务层**: 后端API业务逻辑 
- **数据层**: 数据库存储和区块链接口
- **集成层**: 第三方API集成（TRON、Telegram）

### 2. 微服务设计
- **用户会话服务**: 管理用户状态和会话
- **钱包管理服务**: TRON地址和余额管理
- **订单处理服务**: 能量租赁订单生命周期
- **交易执行服务**: TRON区块链交易处理

### 3. 容错设计
- **API降级**: 主API失败时自动切换备用API
- **数据备份**: 内存存储+本地文件双重保障
- **错误恢复**: 自动重试机制和错误隔离

## 📦 模块架构

### 前端模块 (Telegram Bot)

```
trx-bot/
├── main.py              # 主程序入口，消息路由
├── buy_energy.py        # 闪租页面业务逻辑
├── models.py            # 数据模型和会话管理
├── tron_api.py          # TRON区块链API客户端
├── backend_api_client.py # 后端API客户端封装
└── config.py            # 配置管理
```

#### 关键组件说明

**main.py - 消息路由中心**
```python
class MessageRouter:
    - handle_start_command()     # 启动命令处理
    - handle_callback_query()   # 按钮回调处理
    - route_to_modules()        # 模块路由分发
```

**buy_energy.py - 闪租页核心**
```python
class FlashRentalHandler:
    - show_flash_rental_page()  # 显示闪租页面
    - handle_energy_selection() # 能量数量选择
    - handle_duration_selection() # 时长选择
    - handle_address_management() # 地址管理
    - query_and_update_balance() # 余额查询更新
```

**models.py - 数据管理**
```python
class UserSession:
    - selected_energy: str
    - selected_duration: str  
    - selected_address: str
    - wallet_addresses: List[str]
    - address_balance: Dict
    
class SessionManager:
    - get_session(user_id) -> UserSession
    - update_session(user_id, **kwargs)
    - save_to_file() / load_from_file()
```

### 后端模块 (FastAPI)

```
backend/
├── main.py              # FastAPI应用入口
├── tron_worker.py       # Celery异步任务处理
├── app/
│   ├── api/             # API路由模块
│   │   ├── orders.py    # 订单管理API
│   │   ├── users.py     # 用户管理API  
│   │   ├── wallets.py   # 钱包管理API
│   │   └── supplier_wallets.py # 供应商钱包API
│   ├── models/          # SQLAlchemy数据模型
│   ├── services/        # 业务逻辑服务层
│   │   ├── order_service.py   # 订单处理服务
│   │   ├── user_service.py    # 用户服务
│   │   ├── wallet_service.py  # 钱包服务
│   │   └── tron_service.py    # TRON交易服务
│   ├── database.py      # 数据库配置和连接
│   └── schemas.py       # Pydantic数据验证模型
└── requirements.txt
```

#### 后端架构特点

**三层服务架构**
1. **API Layer** - 接收HTTP请求，参数验证
2. **Service Layer** - 业务逻辑处理，事务管理
3. **Data Layer** - 数据访问，区块链交互

**异步任务处理**
```python
# Celery任务队列
@celery_app.task
def process_energy_order(order_id):
    # 1. 验证订单状态
    # 2. 选择供应商钱包
    # 3. 执行能量委托交易
    # 4. 更新订单状态
```

## 🔄 数据流设计

### 1. 用户交互流程

```
用户点击 → Telegram回调 → Bot处理 → 状态更新 → 界面刷新
    ↓           ↓           ↓         ↓          ↓
Callback   handle_xxx   update_   save_to_   edit_message
 Query      function    session   storage     _text
```

### 2. 余额查询流程

```
用户请求 → Bot调用 → TRON API → 数据解析 → 缓存存储 → 界面显示
   ↓         ↓         ↓         ↓         ↓         ↓
address   tron_api   TronScan   parse_    session   update_
balance   .get_      API        balance   cache     message
         balance
```

### 3. 订单处理流程

```
创建订单 → 后端API → 异步任务 → TRON交易 → 状态更新 → 用户通知
   ↓         ↓         ↓         ↓         ↓         ↓
POST      order_     Celery    tron_     update    Telegram
/orders   service    task      service   database  notification
```

## 🛡️ 安全架构

### 1. 数据安全
- **私钥加密**: Fernet加密算法保护供应商钱包私钥
- **会话隔离**: 用户会话数据完全隔离
- **地址验证**: 多重TRON地址格式验证

### 2. 接口安全
- **输入验证**: Pydantic模型严格验证所有输入
- **异常处理**: 完整的错误处理和日志记录
- **超时控制**: API调用设置合理超时时间

### 3. 业务安全
- **交易幂等**: 防止重复交易执行
- **余额检查**: 交易前严格验证余额充足性
- **回滚机制**: 交易失败自动回滚和退款

## 📊 性能架构

### 1. 缓存策略
```python
# 多层缓存设计
L1: 内存缓存 (会话状态)
L2: Redis缓存 (余额数据) - 可选
L3: 数据库缓存 (持久化数据)
```

### 2. 异步处理
- **非阻塞操作**: 所有TRON API调用异步执行
- **任务队列**: Celery处理耗时操作
- **批量处理**: 批量更新钱包余额和订单状态

### 3. 资源优化
- **连接复用**: HTTP连接池和数据库连接池
- **内存管理**: 定期清理过期会话数据
- **API限制**: 合理控制第三方API调用频率

## 🔧 可扩展架构

### 1. 水平扩展
- **无状态设计**: API服务可水平扩展
- **会话外置**: 支持Redis集群存储会话
- **负载均衡**: 支持多实例部署

### 2. 功能扩展
- **插件架构**: 新功能模块化开发
- **API版本控制**: 支持多版本API共存
- **消息队列**: 支持多种消息队列后端

### 3. 第三方集成
- **API抽象层**: 统一的第三方API接口
- **配置驱动**: 通过配置文件控制集成方式
- **策略模式**: 支持多种支付和交易方式

## 📈 监控架构

### 1. 日志系统
```python
# 分级日志记录
- DEBUG: 详细调试信息
- INFO: 正常业务操作
- WARNING: 潜在问题
- ERROR: 错误异常
- CRITICAL: 系统故障
```

### 2. 指标监控
- **响应时间**: API接口响应时间
- **成功率**: 交易成功率和API调用成功率
- **资源使用**: CPU、内存、磁盘使用情况
- **用户活跃度**: 日活用户和功能使用统计

### 3. 告警机制
- **阈值告警**: 关键指标超过阈值时告警
- **异常告警**: 程序异常和错误告警
- **业务告警**: 交易失败和余额不足告警

## 🔮 未来架构规划

### 短期优化
- **消息队列升级**: 引入RabbitMQ或Kafka
- **缓存优化**: 完整的Redis缓存层
- **API网关**: 统一的API网关和鉴权

### 中期规划
- **微服务拆分**: 按业务域拆分独立服务
- **事件驱动架构**: 基于事件的异步处理
- **容器化部署**: Docker + Kubernetes部署

### 长期愿景
- **多链支持**: 支持其他区块链网络
- **智能决策**: AI驱动的价格优化和风控
- **全球化部署**: 多地域部署和CDN加速

---

*最后更新: 2025-09-12*  
*架构版本: v2.2*