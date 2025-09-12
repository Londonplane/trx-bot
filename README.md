# TRON能量助手 - 完整解决方案

一个功能完整的TRON能量租赁Telegram机器人项目，采用前后端分离架构，包含用户界面、订单管理、钱包池管理和自动化交易执行。

## 🌟 项目特色

- 🤖 **智能Telegram界面**: 直观的能量租赁操作体验
- 🏗️ **企业级后端**: FastAPI + 数据库 + 任务队列完整架构
- ⚡ **真实TRON集成**: 对接TRON网络执行真实能量委托交易
- 🔐 **企业级安全**: 私钥加密、交易幂等、完整错误处理
- 🚀 **生产就绪**: 容器化部署、监控日志、自动化测试

## 📱 核心功能

### Telegram Bot前端
- ✅ **闪租页面**: 能量数量和时长选择，实时成本计算
- ✅ **钱包管理**: 多地址管理、余额查询、地址验证
- ✅ **用户体验**: 消息编辑、状态高亮、加载提示
- ✅ **容错机制**: API降级、错误重试、优雅处理异常

### 后端管理系统
- ✅ **订单管理**: 完整的能量租赁订单生命周期
- ✅ **用户系统**: TRX/USDT余额管理、充值确认、交易记录
- ✅ **供应商钱包池**: 多钱包管理、智能选择、加密存储
- ✅ **TRON交易引擎**: 自动化能量委托交易执行
- ✅ **异步任务**: Celery任务队列处理订单和更新余额

## 🏗️ 技术架构

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Telegram      │    │   FastAPI        │    │   PostgreSQL    │
│   Bot Frontend  │◄──►│   Backend API    │◄──►│   Database      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        
         │              ┌──────────────────┐               
         └──────────────►│   TRON Network   │               
                        │   Blockchain     │               
                        └──────────────────┘               
```

## 🚀 快速开始

### 预备环境
- Python 3.8+
- 数据库 (PostgreSQL/SQLite)
- Redis (可选，用于任务队列)
- Telegram Bot Token

### 一键启动
```bash
# 1. 克隆项目
git clone <repository-url>
cd trx-bot

# 2. 配置Bot Token
cp config.py.example config.py
# 编辑config.py，添加你的BOT_TOKEN

# 3. 启动后端服务
cd backend && ./start_services.sh

# 4. 启动Telegram Bot
cd .. && python main.py
```

**详细指南**: [docs/user/quick_start.md](docs/user/quick_start.md) - 30分钟完成功能测试

## 📁 项目结构

```
trx-bot/
├── main.py                    # Telegram Bot主程序
├── buy_energy.py             # 闪租页面业务逻辑
├── models.py                 # 数据模型和会话管理
├── tron_api.py               # TRON API客户端
├── backend_api_client.py     # 后端API客户端
├── config.py                 # 配置文件
├── backend/                  # 后端API服务
│   ├── main.py              # FastAPI入口
│   ├── tron_worker.py       # Celery任务处理
│   ├── app/                 # 应用核心
│   │   ├── api/            # API路由
│   │   ├── models/         # 数据模型
│   │   └── services/       # 业务逻辑
│   └── requirements.txt
├── tests/                   # 测试代码
│   ├── core/               # 测试基础设施
│   ├── features/           # 功能测试
│   └── docs/               # 测试文档
└── docs/                   # 项目文档
    ├── user/              # 用户文档
    ├── developer/         # 开发者文档
    ├── deployment/        # 部署文档
    └── api/               # API文档
```

## 📚 文档导航

### 👤 用户文档
- [🚀 快速开始](docs/user/quick_start.md) - 30分钟快速体验
- [📖 用户手册](docs/user/user_guide.md) - 详细功能说明
- [🔧 故障排除](docs/user/troubleshooting.md) - 问题解决方案
- [❓ 常见问题](docs/user/faq.md) - FAQ集合

### 👨‍💻 开发者文档  
- [🏗️ 技术架构](docs/developer/architecture.md) - 系统设计详解
- [💻 开发指南](docs/developer/development.md) - 开发环境和规范
- [🗃️ 数据库设计](docs/developer/database_schema.md) - 数据模型说明
- [⚡ TRON集成](docs/developer/tron_integration.md) - 区块链接口
- [📝 开发日志](docs/developer/changelog.md) - 版本变更历史

### 🚀 部署运维
- [🌐 生产部署](docs/deployment/production.md) - 正式环境配置
- [🧪 测试指南](docs/deployment/testing.md) - 测试流程
- [📊 监控运维](docs/deployment/monitoring.md) - 系统监控

### 🔌 API文档
- [📋 接口文档](docs/api/endpoints.md) - 详细API说明
- [🔗 集成指南](docs/api/integration.md) - 使用示例

## 🧪 测试验证

### 运行自动化测试
```bash
# 运行完整测试套件
cd tests && python run_tests.py

# 运行特定功能测试
python tests/features/flash_rental/test_flash_rental_ui.py
```

### API测试示例
```bash
# 健康检查
curl http://localhost:8002/health

# 创建订单
curl -X POST http://localhost:8002/api/orders/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": 123456, "energy_amount": 65000, "duration": "1h", "receive_address": "TR..."}'
```

## 🔐 安全特性

- ✅ **数据安全**: 私钥Fernet加密、会话隔离
- ✅ **接口安全**: 输入验证、异常处理、超时控制  
- ✅ **业务安全**: 交易幂等、余额验证、自动回滚
- ✅ **运营安全**: 完整日志、异常监控、故障告警

## 🎯 版本状态

### 当前版本: v2.2.1 - 完整功能版
- ✅ **Telegram Bot**: 完整的用户界面和交互体验
- ✅ **后端服务**: 15个API端点，完整业务逻辑
- ✅ **TRON集成**: 真实区块链交易执行
- ✅ **测试框架**: 自动化测试和验证工具
- ✅ **生产部署**: 企业级配置和监控

### 下一版本计划
- 🔄 Web管理后台界面
- 🔄 多链支持扩展
- 🔄 智能定价算法
- 🔄 高可用集群部署

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发流程
1. Fork本仓库
2. 创建特性分支
3. 提交更改并添加测试
4. 创建Pull Request

### 开发环境
```bash
# 安装开发依赖
pip install -r requirements.txt
pip install -r tests/requirements.txt

# 运行代码检查
flake8 .
pytest tests/
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 获取支持

- 📖 **文档**: 查看 [docs/](docs/) 目录
- 🐛 **Bug报告**: 提交 [GitHub Issue](../../issues)
- 💡 **功能请求**: 提交 [Feature Request](../../issues)
- 📧 **技术支持**: 查看故障排除指南

---

⭐ **如果这个项目对您有帮助，请给它一个星标！**

*最后更新: 2025-09-12 | 版本: v2.2.1*