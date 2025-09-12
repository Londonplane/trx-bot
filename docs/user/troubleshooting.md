# 故障排除指南

## 🔧 常见问题解决方案

### 🚨 服务启动问题

#### 问题1: 后端服务端口冲突
```
Error: [WinError 10048] 通常每个套接字地址只允许使用一次
```

**解决方案**:
```bash
# 查找占用8002端口的进程
netstat -ano | findstr :8002

# 终止占用端口的进程
taskkill /PID <进程ID> /F

# 或者修改端口配置
# 在 backend/main.py 中修改端口号
```

#### 问题2: Python依赖包冲突
```
ImportError: cannot import name 'xxx' from 'xxx'
```

**解决方案**:
```bash
# 创建虚拟环境
python -m venv trx-bot-env

# 激活虚拟环境
# Windows:
trx-bot-env\Scripts\activate
# Linux/macOS:
source trx-bot-env/bin/activate

# 重新安装依赖
pip install --upgrade pip
pip install -r requirements.txt
```

#### 问题3: 数据库连接失败
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**解决方案**:
```bash
# 检查数据库服务状态
# 对于SQLite（默认），确保有写入权限

# 对于PostgreSQL，检查服务状态
pg_ctl status

# 重置数据库（会清空数据）
rm backend/energy_bot.db  # SQLite
python backend/create_tables.py  # 重建表结构
```

### 🤖 Telegram Bot问题

#### 问题4: Bot Token无效
```
telegram.error.InvalidToken: Invalid token
```

**解决方案**:
1. 检查config.py中的BOT_TOKEN配置
2. 确认Token来自@BotFather
3. Token格式: `数字:字母数字字符串`，如 `123456789:ABCdefGHIjklMNOPqrsTUVwxyz`

#### 问题5: Bot无响应或响应慢
**症状**: 发送消息后Bot不回复或延迟很长时间

**解决方案**:
```bash
# 检查网络连接
ping api.telegram.org

# 检查Bot程序日志
python main.py
# 观察终端输出的错误信息

# 测试API连接
curl -X GET "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe"
```

#### 问题6: 回调按钮无响应
**症状**: 点击按钮后无反应或报错

**解决方案**:
1. 检查callback_data长度（不超过64字符）
2. 确认回调处理函数正确注册
3. 查看终端错误日志
4. 重启Bot程序

### 🔗 TRON API问题

#### 问题7: 余额查询失败
```
Error: Failed to fetch balance for address
```

**解决方案**:
```bash
# 手动测试API连接
curl "https://apilist.tronscan.org/api/account?address=TCX13dZVJt1uCDCGA3F26KqEndpsSt2CHy"

# 检查网络配置
# 确认使用正确的网络（mainnet/shasta）
# config.py中设置：TRON_NETWORK = "shasta"

# 验证地址格式
# Shasta测试网地址示例：TCX13dZVJt1uCDCGA3F26KqEndpsSt2CHy
```

#### 问题8: 地址验证错误
**症状**: 有效地址被拒绝或无效地址被接受

**解决方案**:
1. 检查地址格式（34字符，以T开头）
2. 确认网络匹配（主网vs测试网）
3. 使用标准TRON地址验证库

### 💾 数据存储问题

#### 问题9: 用户会话丢失
**症状**: 重启后用户的地址列表和选择状态消失

**当前状态**: 系统使用内存存储，重启后数据会丢失（这是预期行为）

**临时解决方案**:
- 添加地址后避免频繁重启
- 记录重要的地址以便重新添加

**长期解决方案**:
- 升级到数据库持久化存储
- 实现用户会话恢复功能

#### 问题10: 钱包地址重复添加
**症状**: 同一地址被多次添加到列表

**解决方案**:
当前系统会自动检查重复，如果仍然出现：
1. 重启Bot程序清理会话
2. 重新添加地址
3. 检查地址格式是否有微小差异

### 📱 界面交互问题

#### 问题11: 消息编辑失败
```
telegram.error.BadRequest: Message is not modified
```

**解决方案**:
这通常是正常的，表示消息内容没有变化。可以忽略此错误。

#### 问题12: 按钮状态不更新
**症状**: 点击按钮后状态图标（🔸🔹）不变化

**解决方案**:
1. 等待2-3秒，Telegram有时有延迟
2. 重新点击按钮
3. 如果持续问题，重启Bot程序

### 🔍 调试技巧

#### 启用详细日志
```python
# 在main.py开头添加
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

#### 检查服务状态
```bash
# 检查后端API健康状态
curl http://localhost:8002/health

# 检查Bot程序运行状态
ps aux | grep python  # Linux/macOS
tasklist | findstr python  # Windows

# 检查端口监听状态
netstat -an | grep 8002  # Linux/macOS
netstat -an | findstr 8002  # Windows
```

#### API测试工具
```bash
# 测试余额查询API
curl "http://localhost:8002/api/users/123456/balance"

# 测试订单创建API
curl -X POST "http://localhost:8002/api/orders/" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 123456, "energy_amount": 65000, "duration": "1h", "receive_address": "TCX13dZVJt1uCDCGA3F26KqEndpsSt2CHy"}'
```

## 🆘 紧急情况处理

### 完全重置
如果所有方法都无效，可以完全重置：

```bash
# 1. 停止所有相关进程
pkill -f "python main.py"
pkill -f "python backend"

# 2. 清理临时文件
rm -rf __pycache__/
rm -rf backend/__pycache__/
rm backend/*.db

# 3. 重新安装依赖
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# 4. 重新启动
cd backend && python main.py &
cd .. && python main.py
```

### 获取技术支持

如果问题仍未解决：

1. **收集信息**:
   - 错误消息的完整文本
   - 操作步骤
   - 系统环境（OS, Python版本）
   - 日志文件内容

2. **查看文档**:
   - [开发指南](../developer/development.md)
   - [技术架构](../developer/architecture.md)
   - [API文档](../api/endpoints.md)

3. **提交Issue**:
   在GitHub仓库提交详细的bug报告

4. **临时解决方案**:
   - 使用Mock数据进行基本功能测试
   - 降级到之前的稳定版本
   - 在虚拟机或容器中隔离测试

## 📊 性能监控

### 监控指标
- API响应时间 < 3秒
- 内存使用量 < 500MB
- 错误率 < 5%

### 性能优化建议
1. 定期重启Bot程序清理内存
2. 监控TRON API调用频率
3. 合理设置超时时间
4. 使用连接池优化数据库访问

---

*最后更新: 2025-09-12*