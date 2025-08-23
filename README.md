# TRON能量助手项目

一个功能完整的TRON能量供应商Telegram机器人及后台管理系统。

## 项目概述

- **前端**: Telegram Bot - 用户通过Telegram界面管理钱包和购买能量
- **后端**: FastAPI服务 - 处理订单、管理钱包池、用户账户系统
- **数据库**: PostgreSQL - 存储用户、订单、钱包等业务数据

## 核心功能

### Telegram Bot (已完成)
- ✅ 钱包地址管理 (添加/删除/选择)
- ✅ 实时TRON余额查询 (TRX/Energy/Bandwidth)
- ✅ 闪租页面 (能量数量和时长选择)
- ✅ 地址验证和错误处理
- ✅ 双API容错机制 (TronScan + 官方API)

### 后端管理系统 (开发中)
- 🔄 订单管理API - 处理真实的能量租赁订单
- 🔄 用户余额系统 - 替换Mock数据，实现真实充值
- ⏳ 供应商钱包池 - 管理多个钱包和Energy库存
- ⏳ 监控报警系统 - 7x24小时运营监控
- ⏳ 管理员界面 - Web管理后台

## 技术架构

### Bot端
- **Python 3.8+** + python-telegram-bot
- **TronScan API** + 官方TRON API
- **JSON文件存储** (临时，将迁移到数据库)

### 后端服务
- **FastAPI** - 高性能异步Web框架
- **PostgreSQL** - 主数据库
- **Redis** - 缓存和任务队列
- **Celery** - 异步任务处理
- **tronpy** - TRON区块链交互

## 快速开始

### 1. 启动Telegram Bot
```bash
pip install -r requirements.txt
python main.py
```

### 2. 启动后端服务
```bash
cd backend
pip install -r requirements.txt
python main.py
```

访问API文档: http://localhost:8000/docs

## 项目结构

```
trx-bot/
├── main.py                    # Telegram Bot主程序
├── buy_energy.py             # 闪租页面业务逻辑
├── models.py                 # 数据模型和会话管理
├── tron_api.py               # TRON API客户端
├── backend_api_client.py     # 后端API客户端
├── config.py                 # Bot配置文件
├── requirements.txt          # Bot依赖包
├── backend/                  # 后端API服务
│   ├── main.py              # FastAPI应用入口
│   ├── app/                 # 应用核心代码
│   │   ├── api/            # API路由
│   │   ├── models/         # 数据库模型
│   │   ├── services/       # 业务逻辑
│   │   └── schemas.py      # 数据验证模型
│   └── requirements.txt    # 后端依赖包
├── docs/                    # 项目文档
└── tests/                   # 测试代码
```

## 开发进度

- [x] **阶段1**: Telegram Bot基础功能完成
- [x] **阶段2**: 后台管理系统设计完成  
- [ ] **阶段3**: 后端API开发 (进行中)
- [ ] **阶段4**: 真实交易功能集成
- [ ] **阶段5**: 监控和管理界面

详细开发记录见: [docs/开发日志.md](docs/开发日志.md)

## 安全特性

- ✅ 只执行查询操作，不涉及私钥存储
- ✅ 地址格式验证，防止无效输入  
- ✅ API错误隔离和容错处理
- 🔄 钱包私钥加密存储 (开发中)
- ⏳ 交易监控和风控系统 (计划中)

## 联系方式

如有问题请提交Issue或联系开发团队。

---

*这是一个生产就绪的TRON能量供应商服务项目*