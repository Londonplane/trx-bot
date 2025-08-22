# TRON能量助手 Telegram机器人

一个专为TRON区块链设计的Telegram机器人，提供能量租赁、套餐购买和余额管理等功能。

## 🌟 主要功能

### ⚡ 闪租 (Buy Energy)
- **时长选择**: 1h / 1d / 3d / 7d / 14d
- **能量预设**: 65K / 135K / 270K / 540K / 1M 
- **自定义数量**: 支持1,000-10,000,000范围内任意能量值
- **实时定价**: 基于选择参数动态计算成本
- **智能界面**: 根据选择状态动态调整按钮布局
- **一键复制**: 支持BUY命令一键复制功能

### 🎯 地址管理
- **多地址支持**: 管理多个TRON接收地址
- **地址验证**: 自动验证TRON地址格式
- **余额查询**: 实时显示地址TRX和ENERGY余额
- **简化显示**: 地址自动简化为易读格式

### 💰 余额管理
- **账户余额**: 显示用户TRX/USDT余额
- **地址余额**: 查询特定地址的链上余额
- **实时更新**: 支持手动刷新余额信息

### 📋 其他功能
- **笔数套餐**: 交易次数套餐（规划中）
- **能量计算器**: 能量需求计算工具（规划中）
- **余额充值**: 账户余额充值功能（规划中）
- **能量代付**: 代他人支付能量费用（规划中）
- **行情查询**: 实时市场价格查询（规划中）

## 🚀 快速开始

### 环境要求
- Python 3.8+
- python-telegram-bot 20.7

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/your-username/trx-bot.git
   cd trx-bot
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置机器人**
   - 在 @BotFather 创建新的Telegram机器人
   - 获取Bot Token
   - 创建 `config.py` 文件：
   ```python
   BOT_TOKEN = "your_bot_token_here"
   ```

4. **启动机器人**
   ```bash
   python main.py
   ```

## 📱 使用说明

### 基本操作
1. 在Telegram中搜索您的机器人
2. 发送 `/start` 开始使用
3. 点击"⚡ Buy Energy（闪租）"进入主要功能

### 闪租流程
1. **选择时长**: 点击时长按钮选择租赁期间
2. **选择能量**: 选择预设能量值或使用"Other amount"自定义
3. **选择地址**: 选择接收地址或添加新地址
4. **确认支付**: 检查订单详情并确认支付

### 特殊功能
- **一键复制**: 点击蓝色命令文本可复制到剪贴板
- **余额刷新**: 点击"Address balance"实时查询地址余额
- **菜单快捷**: 使用文本框左侧的菜单按钮快速访问功能

## 🏗️ 项目结构

```
trx-bot/
├── main.py                 # 主程序入口
├── buy_energy.py          # 闪租页核心逻辑
├── models.py              # 数据模型和会话管理
├── config.py              # 配置文件
├── requirements.txt       # 依赖包列表
├── CLAUDE.md             # Claude开发指南
├── README.md             # 项目说明文档
└── docs/                 # 详细文档
    ├── 闪租页实现总结.md
    ├── 闪租页（Buy Energy）交互与开发规格文档.md
    ├── 主页面信息卡片布局方案.md
    ├── 功能模块.md
    └── 启动说明.md
```

## 🔧 技术特性

### 架构设计
- **会话状态管理**: 基于内存的用户状态存储
- **消息编辑机制**: 单消息内完成所有交互，保持界面整洁
- **回调路由系统**: 基于前缀的回调处理分发
- **模块化设计**: 功能模块独立，易于扩展维护

### 用户体验优化
- **智能按钮布局**: 根据选择状态动态调整界面
- **实时反馈**: 参数变更立即更新显示
- **错误处理**: 全面的输入验证和错误提示
- **加载提示**: 异步操作的友好提示信息

### 技术亮点
- **Markdown支持**: 全面支持Markdown格式解析
- **一键复制**: 利用Telegram内置功能实现命令复制
- **状态高亮**: 🔸🔹图标区分不同类型的选择状态
- **临时消息管理**: 自动清理临时提示消息

## 📊 Demo数据

当前版本使用Mock数据进行演示：

### 预设地址
- `TRX9Uhjn948ynC8J2LRRHVpbdYT6GKRTLz`
- `TBrLXQs4q2XQ29dGFbyiTCcvXuN2tGJvSK`
- `TNRLJjF9uGp2gZMZVQWcJSkbKnH7wdvGRw`

### 定价算法
```python
base_price = energy_value * 0.00001
time_multiplier = duration_days * 0.8
total_cost = base_price * time_multiplier
```

### 默认设置
- 初始余额: 20.000 TRX
- 默认选择: 1h + 65K能量
- 地址余额: 随机生成 15-25 TRX

## 🔮 后续规划

### 短期目标
- [ ] 集成真实TRON API
- [ ] 实现数据库存储
- [ ] 完善其他功能模块
- [ ] 添加多语言支持

### 长期目标
- [ ] 支付系统集成
- [ ] 用户等级系统
- [ ] 订单历史管理
- [ ] 高级统计功能

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发流程
1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

### 代码规范
- 遵循PEP 8代码风格
- 添加适当的注释和文档
- 确保所有功能都经过测试

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 [Issue](https://github.com/your-username/trx-bot/issues)
- 发送邮件到: your-email@example.com

## 🙏 致谢

感谢所有为本项目做出贡献的开发者和用户！

---

⭐ 如果这个项目对您有帮助，请给它一个星标！