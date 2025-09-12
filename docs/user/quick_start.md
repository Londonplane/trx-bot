# 快速开始指南

## 🚀 30分钟快速体验

这是一个TRON能量助手Telegram机器人项目，包含前端Bot和后端API服务。按照本指南，您可以在30分钟内完成所有核心功能的测试体验。

## 📋 环境要求

- **Python**: 3.8+
- **操作系统**: Windows 10/11, macOS, Linux
- **网络**: 稳定的网络连接（访问TRON API和Telegram API）

## ⚡ 最快启动方式

### 步骤1: 准备项目
```bash
# 克隆项目（如果还没有）
git clone <repository-url>
cd trx-bot

# 安装依赖
pip install -r requirements.txt
```

### 步骤2: 配置Telegram Bot
1. 在Telegram中搜索 `@BotFather`
2. 发送 `/newbot` 创建新机器人
3. 按提示设置机器人名称和用户名
4. 获取Bot Token
5. 创建配置文件：
```python
# config.py
BOT_TOKEN = "your_bot_token_here"
TRON_NETWORK = "shasta"  # 使用测试网
```

### 步骤3: 启动后端服务
```bash
# 进入后端目录
cd backend

# Windows用户
start_services.bat

# Linux/macOS用户
./start_services.sh

# 验证服务启动
curl http://localhost:8002/health
# 应该返回: {"status":"healthy"}
```

### 步骤4: 启动Telegram Bot
```bash
# 返回项目根目录
cd ..

# 启动Bot
python main.py
```

如果看到 "Application started" 消息，说明启动成功！

## 🎯 功能测试流程

### 1. 基础测试（5分钟）
1. 在Telegram中搜索您的机器人
2. 发送 `/start` 命令
3. 点击 "⚡ Flash rental" 按钮
4. 验证界面正常显示

### 2. 参数选择测试（5分钟）
1. 尝试点击不同的能量数量按钮（65K, 135K等）
2. 尝试点击不同的时长按钮（1h, 1d等）
3. 观察按钮状态变化（🔸🔹图标）
4. 尝试 "Other amount" 自定义输入

### 3. 地址管理测试（10分钟）
1. 点击 "Select address" 按钮
2. 添加测试地址（推荐使用测试钱包地址）：
   - `TCX13dZVJt1uCDCGA3F26KqEndpsSt2CHy`
   - `TAcrAuU78UyPZpZuVPCQo2ZVcfwmkskWLz`
3. 验证地址格式检查功能
4. 在不同地址间切换

### 4. 余额查询测试（10分钟）
1. 选择一个地址后，点击 "Address balance" 按钮
2. 观察加载提示：🔄 Updating balance…
3. 查看余额信息显示：
   ```
   ℹ️ Address balance:
   TRX: xxx.xxx
   ENERGY: xxx
   BANDWIDTH: xxx
   ```
4. 验证成本计算是否正确显示

## ✅ 验证清单

完成测试后，请确认以下功能正常：

- [ ] 后端服务启动成功（localhost:8002/health 返回正常）
- [ ] Telegram Bot 响应 `/start` 命令
- [ ] 闪租页界面正常显示
- [ ] 能量数量和时长选择功能正常
- [ ] 地址添加和验证功能正常
- [ ] 余额查询显示真实数据
- [ ] 成本计算显示合理结果
- [ ] 所有按钮交互正常响应

## 🔧 常见问题

### Q1: 后端服务启动失败
**解决方案**:
```bash
# 检查端口是否被占用
netstat -an | grep 8002

# 手动启动后端
cd backend
python main.py
```

### Q2: Bot无响应
**解决方案**:
- 检查Bot Token是否正确配置
- 确认网络连接正常
- 查看终端错误日志

### Q3: 余额查询显示0或失败
**解决方案**:
- 确认使用Shasta测试网地址
- 检查TRON API网络连接
- 验证地址格式是否正确

### Q4: 依赖包安装失败
**解决方案**:
```bash
# 升级pip
pip install --upgrade pip

# 使用镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

## 🎯 下一步

完成基本测试后，您可以：

1. **深入了解功能**: 查看 [用户手册](user_guide.md)
2. **参与开发**: 查看 [开发指南](../developer/development.md)
3. **部署到生产**: 查看 [生产部署](../deployment/production.md)
4. **API集成**: 查看 [API文档](../api/endpoints.md)

## 📞 获取帮助

如果遇到问题：
- 查看 [故障排除指南](troubleshooting.md)
- 查看 [常见问题FAQ](faq.md)
- 提交 GitHub Issue
- 查看详细的开发日志和技术文档

---

🎉 **恭喜！** 您已成功完成TRON能量助手的快速体验！

*最后更新: 2025-09-12*