# 测试代码

## 概述
TRON能量助手项目的自动化测试代码，确保系统稳定性和代码质量。

## 测试层次
- **单元测试**: 测试核心业务逻辑和工具函数
- **集成测试**: 测试API接口和数据库交互
- **端到端测试**: 测试完整的用户流程
- **压力测试**: 验证系统性能和并发处理能力

## 测试框架
- pytest (Python测试框架)
- pytest-asyncio (异步测试支持)
- httpx (异步HTTP客户端测试)
- factory_boy (测试数据生成)

## 测试目录结构
```
tests/
├── unit/           # 单元测试
├── integration/    # 集成测试  
├── e2e/           # 端到端测试
├── performance/   # 性能测试
└── fixtures/      # 测试数据和夹具
```

## 运行测试
```bash
# 运行所有测试
pytest

# 运行特定模块测试
pytest tests/unit/

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

## 开发状态
待开发 - 随后台系统开发同步进行