# 测试目录结构说明

## 📁 目录结构

```
tests/
├── README.md           # 本说明文件
├── core/               # 全局测试资源和配置
│   ├── test_config.py  # 测试配置和常量
│   ├── test_wallets.py # 测试钱包管理
│   ├── test_utils.py   # 测试工具函数
│   ├── fixtures.py     # 测试数据装置
│   ├── test_api_connection.py # API连接测试 (历史)
│   └── api_connection_test_legacy.py # API连接测试备份
├── features/           # 功能模块测试
│   ├── flash_rental/   # 闪租页功能测试
│   │   ├── __init__.py
│   │   ├── test_flash_rental_ui.py
│   │   ├── test_balance_query.py
│   │   └── test_energy_calculation.py
│   ├── wallet_management/  # 钱包管理测试 (未来)
│   └── order_system/       # 订单系统测试 (未来)
├── resources/          # 测试资源文件
│   ├── wallets.json    # 测试钱包数据
│   ├── mock_data.json  # 模拟测试数据
│   └── test_scenarios.json # 测试场景配置
├── results/            # 测试结果输出
│   ├── latest/         # 最新测试结果
│   └── history/        # 历史测试记录
└── docs/               # 测试文档
    ├── flash_rental_test_manual.md
    ├── business_flow_guide.md
    ├── testing_standards.md
    ├── business_flow_test.py           # 业务流程测试脚本
    ├── comprehensive_test_plan_legacy.md # 完整测试计划 (历史)
    └── business_flow_test_legacy.py    # 业务流程测试备份
```

## 🎯 设计原则

### 1. 分离关注点
- **core/**: 全局性的测试基础设施，被所有测试模块共享
- **features/**: 按功能模块组织的具体测试代码
- **resources/**: 测试数据和配置资源，版本控制友好
- **results/**: 测试结果输出，便于分析和历史对比
- **docs/**: 测试相关文档，支持手动测试和自动化测试

### 2. 可扩展性
- 每个功能模块都有独立的测试目录
- 测试资源统一管理，避免重复
- 支持多种测试类型：单元测试、集成测试、端到端测试

### 3. 维护性
- 清晰的目录结构和命名规范
- 统一的测试配置和工具函数
- 完善的文档和示例

## 🚀 快速开始

### 运行闪租页功能测试
```bash
cd tests
python -m features.flash_rental.test_flash_rental_ui
```

### 查看测试结果
```bash
# 最新测试结果
cat results/latest/test_report.json

# 历史测试记录
ls results/history/
```

## 📊 当前状态

- ✅ **目录结构**: 已完成基础框架
- ✅ **核心资源**: 测试钱包和配置已整理  
- ✅ **闪租页测试**: 已迁移并优化
- ⏳ **其他功能**: 待后续开发时补充

## 🔧 测试环境要求

- Python 3.8+
- 后端API服务运行在 localhost:8002
- TRON网络连接（Shasta测试网）
- Telegram Bot服务（用于UI测试）