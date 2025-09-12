# 🚀 TRON能量助手本地测试快速清单

## 📋 测试前准备检查

### 本地环境准备
- [ ] Windows 10/11 系统
- [ ] Python 3.8+ 已安装
- [ ] 项目代码已在本地 (C:\Users\wt200\trx-bot)
- [ ] 网络连接正常 (可访问TRON网络)

### 资金准备 ⚠️ 仅使用测试资金
- [ ] 准备2-3个供应商钱包，各100+ TRX
- [ ] 准备测试用户钱包地址
- [ ] 记录所有私钥 (测试后立即销毁)

### 配置文件准备
- [ ] Telegram Bot Token
- [ ] TRON API Key (可选)
- [ ] 强随机密钥生成

---

## 🔧 阶段1: 本地环境部署 (预计15分钟)

### 环境配置
```cmd
# 1. 打开命令提示符 (以管理员身份)
# 进入项目目录
cd C:\Users\wt200\trx-bot

# 2. 配置后端环境
cd backend
copy .env.example .env
# 编辑 .env 文件，填入必要配置
```

### 依赖安装和服务启动
```cmd
# 3. 安装后端依赖
pip install -r requirements.txt

# 4. 启动后端服务 (使用现有脚本)
start_services.bat
```

### ✅ 验证步骤
```cmd
# 等待服务启动 (约30秒)
# 新开一个命令行窗口测试

# 测试API健康状态 (使用PowerShell)
powershell -Command "Invoke-RestMethod -Uri 'http://localhost:8002/health'"
# 期望: status=healthy

# 或使用浏览器访问
# http://localhost:8002/health
# http://localhost:8002/docs (API文档)
```

**验收标准**: 所有API调用返回正确响应 ✅

---

## 💳 阶段2: 钱包配置 (预计15分钟)

### 添加供应商钱包
```powershell
# 1. 添加第一个钱包 (PowerShell)
$body = @{
    private_key = "your_64_char_private_key_here"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8002/api/supplier-wallets/add" -Method POST -Body $body -ContentType "application/json"

# 2. 验证钱包添加
Invoke-RestMethod -Uri "http://localhost:8002/api/supplier-wallets/"
```

### ✅ 验证步骤
- [ ] 钱包地址正确显示
- [ ] TRX余额显示正确 (应该>50 TRX)
- [ ] Energy余额显示正确
- [ ] 钱包状态为 `"is_active": true`

**验收标准**: 钱包信息完整准确，余额>50 TRX ✅

---

## 💰 阶段3: 用户充值测试 (预计10分钟)

### 模拟用户充值
```powershell
# 1. 创建测试用户充值 (PowerShell)
$body = @{
    tx_hash = "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    amount = 20.0
    currency = "TRX"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8002/api/users/999888/deposit" -Method POST -Body $body -ContentType "application/json"

# 2. 验证用户余额
Invoke-RestMethod -Uri "http://localhost:8002/api/users/999888/balance"
```

### ✅ 验证步骤
- [ ] 充值接口返回 `"success": true`
- [ ] 用户余额显示 `"balance_trx": "20.000000"`
- [ ] 余额变动有记录

**验收标准**: 用户充值成功，余额更新正确 ✅

---

## 🛒 阶段4: 订单流程测试 (预计20分钟)

### 创建测试订单
```powershell
# 1. 创建订单 (PowerShell)
$body = @{
    user_id = 999888
    energy_amount = 32000
    duration = "1h"
    receive_address = "你的测试接收地址(42字符)"
} | ConvertTo-Json

$orderResponse = Invoke-RestMethod -Uri "http://localhost:8002/api/orders/" -Method POST -Body $body -ContentType "application/json"
$orderResponse

# 2. 记录订单ID并手动查询状态
$orderId = $orderResponse.id
echo "Order ID: $orderId"

# 查询订单状态 (重复执行观察变化)
Invoke-RestMethod -Uri "http://localhost:8002/api/orders/$orderId"
```

### ✅ 验证步骤
- [ ] 订单创建成功，返回订单ID
- [ ] 订单状态从 `pending` 变为 `processing`
- [ ] 用户余额被正确扣减 (约0.021 TRX)
- [ ] 订单最终状态为 `completed` (或观察处理过程)

### 🎯 关键观察点
```powershell
# 打开多个PowerShell窗口进行监控

# 窗口1: 订单状态监控
while($true) {
    $order = Invoke-RestMethod -Uri "http://localhost:8002/api/orders/$orderId"
    Write-Host "$(Get-Date): Status=$($order.status), Error=$($order.error_message)"
    Start-Sleep 5
}

# 窗口2: 用户余额监控
while($true) {
    $balance = Invoke-RestMethod -Uri "http://localhost:8002/api/users/999888/balance"
    Write-Host "$(Get-Date): Balance=$($balance.balance_trx)"
    Start-Sleep 5
}

# 窗口3: 钱包池状态监控
while($true) {
    $wallets = Invoke-RestMethod -Uri "http://localhost:8002/api/supplier-wallets/"
    Write-Host "$(Get-Date): Energy=$($wallets[0].energy_available), TRX=$($wallets[0].trx_balance)"
    Start-Sleep 5
}
```

**验收标准**: 订单成功处理，余额正确扣减，TRON交易执行 ✅

---

## 🤖 阶段5: Telegram Bot测试 (预计15分钟)

### Bot服务启动
```cmd
# 1. 启动Bot (新的命令行窗口)
cd C:\Users\wt200\trx-bot
python main.py
```

### 端到端测试流程
1. **启动Bot**: 在Telegram中发送 `/start`
2. **添加钱包**: 添加测试接收地址
3. **余额查询**: 点击 "Address balance" 验证TRON余额查询
4. **闪租页面**: 选择 "32K Energy, 1h" 
5. **费用确认**: 验证费用计算 (约0.021 TRX)
6. **下单测试**: 点击 "Buy" 按钮
7. **状态跟踪**: 观察订单处理过程

### ✅ 验证步骤
- [ ] Bot正常启动和响应
- [ ] 钱包地址验证功能正常  
- [ ] 余额查询显示真实数据
- [ ] 费用计算准确
- [ ] 下单流程完整
- [ ] 订单状态正确显示

**验收标准**: 端到端用户流程完全正常 ✅

---

## ⚡ 阶段6: 性能测试 (预计10分钟)

### 基础性能测试
```powershell
# 1. API响应时间测试
Measure-Command { Invoke-RestMethod -Uri "http://localhost:8002/health" }

# 2. 并发订单测试 (3个并发订单) - 简化版
for($i=1; $i -le 3; $i++) {
    $body = @{
        user_id = 999888 + $i
        energy_amount = 16000
        duration = "1h"
        receive_address = "你的测试接收地址"
    } | ConvertTo-Json
    
    Start-Job -ScriptBlock {
        param($body)
        Invoke-RestMethod -Uri "http://localhost:8002/api/orders/" -Method POST -Body $body -ContentType "application/json"
    } -ArgumentList $body
}

# 3. 检查作业状态
Get-Job | Receive-Job
```

### ✅ 验证步骤
- [ ] API响应时间 < 2秒
- [ ] 并发订单正常处理
- [ ] 系统资源使用正常 (内存<80%, 磁盘<80%)
- [ ] 无明显性能瓶颈

**验收标准**: 系统性能满足基本要求 ✅

---

## 🔒 阶段7: 安全检查 (预计5分钟)

### 安全验证测试
```cmd
# 1. 检查私钥加密存储
cd C:\Users\wt200\trx-bot\backend
python -c "from app.models import SupplierWallet; from app.database import SessionLocal; db = SessionLocal(); wallet = db.query(SupplierWallet).first(); print('Private key encrypted length:', len(wallet.private_key_encrypted) if wallet else 'No wallet'); print('Private key starts with:', wallet.private_key_encrypted[:20] if wallet else 'N/A')"
```

```powershell
# 2. 测试API错误处理
$invalidBody = @{invalid = "data"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8002/api/orders/" -Method POST -Body $invalidBody -ContentType "application/json"
```

### ✅ 验证步骤
- [ ] 私钥已加密存储 (不是明文)
- [ ] 无效请求返回适当错误，不崩溃
- [ ] 日志中无敏感信息泄露
- [ ] 服务稳定运行

**验收标准**: 基本安全机制工作正常 ✅

---

## 📊 最终验收检查

### 核心功能验收 ✅
- [ ] **API服务**: 所有端点正常响应
- [ ] **数据库**: 数据正确存储和查询  
- [ ] **钱包管理**: 供应商钱包正常工作
- [ ] **用户系统**: 充值和余额管理正常
- [ ] **订单处理**: 完整的订单生命周期
- [ ] **Telegram Bot**: 端到端用户体验良好
- [ ] **TRON集成**: 真实区块链交互 (如果网络可达)

### 性能和稳定性 ✅  
- [ ] **响应时间**: API平均响应 < 2秒
- [ ] **并发处理**: 支持多个订单并行处理
- [ ] **资源使用**: 内存和磁盘使用合理
- [ ] **错误处理**: 异常情况优雅处理

### 业务流程 ✅
- [ ] **用户注册**: 新用户可以正常使用
- [ ] **充值流程**: 充值确认和余额更新
- [ ] **下单流程**: 完整的能量租赁流程
- [ ] **订单跟踪**: 状态更新和通知
- [ ] **退款机制**: 失败订单自动退款

---

## 🚨 紧急问题处理

### 如果测试失败

#### API服务无法启动
```bash
# 检查日志
tail -f /var/log/syslog | grep python

# 检查端口占用
netstat -tlnp | grep 8002

# 重启服务
pkill -f "python3 main.py"
cd backend && python3 main.py
```

#### 订单处理失败
```bash
# 检查供应商钱包余额
curl http://localhost:8002/api/supplier-wallets/

# 手动处理pending订单
curl -X POST http://localhost:8002/api/supplier-wallets/process-orders

# 检查TRON网络连通性
python3 -c "from tronpy import Tron; print(Tron().get_latest_block_number())"
```

#### Bot无响应
```bash
# 重启Bot服务
pkill -f "main.py"
cd /root/trx-bot && python3 main.py

# 检查Bot Token
grep TELEGRAM_BOT_TOKEN backend/.env
```

---

## ✨ 测试成功后的下一步

### 生产环境优化
1. **配置HTTPS** - 使用Nginx + Let's Encrypt
2. **设置systemd服务** - 自动启动和重启  
3. **配置监控** - 日志监控和报警
4. **备份策略** - 定期数据库备份
5. **安全加固** - 防火墙、更新密钥

### 业务准备
1. **资金管理** - 供应商钱包充值策略
2. **定价策略** - 根据市场调整价格
3. **客服准备** - 处理用户问题和投诉
4. **营销推广** - 用户获取和留存

### 监控维护
1. **7x24监控** - 服务可用性监控
2. **性能监控** - 响应时间和资源使用
3. **业务监控** - 订单量、成功率、收入
4. **安全监控** - 异常访问和攻击检测

---

## 📞 支持联系

如果在测试过程中遇到问题：

1. **查看日志文件** - 检查详细错误信息
2. **参考故障排查指南** - `docs/正式场景测试指南.md`
3. **GitHub Issues** - 提交具体的问题描述
4. **技术文档** - 查阅 `docs/` 目录下的所有文档

---

**预计总测试时间**: 2-3小时  
**建议测试人数**: 2人 (一人操作，一人记录)  
**最佳测试时间**: 工作日白天，便于处理问题  

🎯 **测试成功标志**: 能够通过Telegram Bot成功购买Energy并在TRON网络上看到真实的委托交易！