# TRON能量助手正式场景测试指南

## 概述

本指南详细说明如何在真实环境中测试TRON能量助手系统，从开发环境迁移到生产环境，并进行端到端的业务流程验证。

---

## 测试前准备

### 1. 环境要求检查

#### 服务器环境
- **VPS规格**: 至少2核4G内存，50G存储
- **操作系统**: Ubuntu 20.04+ 或 CentOS 8+
- **网络**: 稳定的外网连接，支持访问TRON网络
- **域名**: 可选，用于HTTPS访问

#### 必需软件
```bash
# 检查Python版本
python3 --version  # 需要3.8+

# 检查Docker (推荐)
docker --version
docker-compose --version

# 检查PostgreSQL (如不使用Docker)
psql --version

# 检查Redis (如不使用Docker)  
redis-cli --version
```

### 2. 资金和钱包准备

#### 供应商钱包 (关键)
- **数量**: 建议准备2-3个TRON钱包
- **资金**: 每个钱包至少100 TRX用于测试
- **能量**: 每个钱包需要有足够的Energy用于委托
- **私钥**: 安全保管，测试完成后立即更换

#### 测试用户钱包
- **用户钱包**: 准备1-2个用于接收能量的钱包地址
- **充值钱包**: 准备用于充值测试的TRX

#### 安全提醒
⚠️ **重要**: 仅使用测试资金，不要使用大额资金进行测试

---

## 阶段1: 服务器部署测试

### 1.1 VPS准备和部署

#### 购买和配置VPS
```bash
# 推荐云服务商配置
# 阿里云/腾讯云/AWS: 2核4G，Ubuntu 20.04
# 带宽: 至少5Mbps
# 存储: 50G SSD

# 连接到VPS
ssh root@your-vps-ip

# 更新系统
apt update && apt upgrade -y

# 安装必要软件
apt install -y git python3 python3-pip nginx certbot
```

#### 部署应用代码
```bash
# 克隆项目代码
git clone https://github.com/your-username/trx-bot.git
cd trx-bot

# 设置环境变量
cp backend/.env.example backend/.env
nano backend/.env
```

#### 生产环境配置 (.env)
```bash
# 数据库配置 - 使用PostgreSQL
DATABASE_URL=postgresql://trx_user:secure_password@localhost:5432/trx_energy

# Redis配置
REDIS_URL=redis://localhost:6379

# 安全密钥 - 使用强密钥
SECRET_KEY=your-super-secure-random-32-character-key
ENCRYPTION_KEY=your-fernet-encryption-key-base64

# TRON网络配置
TRON_NETWORK=mainnet
TRON_API_KEY=your-tron-api-key-optional

# Telegram Bot配置
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_WEBHOOK_URL=https://your-domain.com/webhook
```

### 1.2 数据库部署

#### 使用Docker部署 (推荐)
```bash
cd backend
docker-compose up -d db redis

# 等待服务启动
sleep 30

# 检查服务状态
docker-compose ps
```

#### 手动部署PostgreSQL
```bash
# 安装PostgreSQL
apt install -y postgresql postgresql-contrib

# 创建数据库和用户
sudo -u postgres psql << EOF
CREATE DATABASE trx_energy;
CREATE USER trx_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE trx_energy TO trx_user;
\q
EOF
```

### 1.3 应用服务部署

#### 安装Python依赖
```bash
cd backend
pip3 install -r requirements.txt

# 测试数据库连接
python3 -c "from app.database import engine; print('Database connection OK')"
```

#### 启动后端服务
```bash
# 使用自动化脚本
chmod +x start_services.sh
./start_services.sh

# 或使用systemd服务 (生产推荐)
# 创建服务文件
sudo tee /etc/systemd/system/trx-backend.service << EOF
[Unit]
Description=TRON Energy Backend Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/trx-bot/backend
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启用并启动服务
sudo systemctl daemon-reload
sudo systemctl enable trx-backend
sudo systemctl start trx-backend
```

### 1.4 服务验证测试

```bash
# 检查API服务状态
curl -X GET http://localhost:8002/health
# 期望响应: {"status":"healthy","message":"API服务正常运行"}

# 检查API文档
curl -X GET http://localhost:8002/docs
# 期望: 返回OpenAPI文档页面

# 检查数据库连接
curl -X GET http://localhost:8002/api/users/12345/balance
# 期望响应: {"user_id":12345,"balance_trx":"0.000000","balance_usdt":"0.000000"}
```

---

## 阶段2: 供应商钱包配置测试

### 2.1 添加供应商钱包

#### 准备钱包信息
```bash
# 查看当前钱包池
curl -X GET http://localhost:8002/api/supplier-wallets/

# 添加第一个供应商钱包
curl -X POST http://localhost:8002/api/supplier-wallets/add \
  -H "Content-Type: application/json" \
  -d '{
    "private_key": "your_supplier_wallet_private_key_64_chars"
  }'

# 期望响应: 钱包信息，包含地址、余额、能量等
```

#### 验证钱包添加结果
```bash
# 再次查看钱包池
curl -X GET http://localhost:8002/api/supplier-wallets/

# 应该看到钱包地址、TRX余额、Energy可用量等信息
# 示例响应:
# [{
#   "id": 1,
#   "wallet_address": "TKx...abc",
#   "trx_balance": "100.000000",
#   "energy_available": 50000,
#   "is_active": true
# }]
```

### 2.2 钱包功能测试

#### 余额更新测试
```bash
# 手动更新所有钱包余额
curl -X POST http://localhost:8002/api/supplier-wallets/update-balances

# 检查更新结果
curl -X GET http://localhost:8002/api/supplier-wallets/
```

#### 钱包状态管理测试
```bash
# 禁用钱包
curl -X PUT http://localhost:8002/api/supplier-wallets/1/toggle

# 启用钱包
curl -X PUT http://localhost:8002/api/supplier-wallets/1/toggle
```

---

## 阶段3: 用户充值流程测试

### 3.1 模拟用户充值

#### 创建测试用户并充值
```bash
# 模拟用户充值 - 使用真实的TRON交易哈希
curl -X POST http://localhost:8002/api/users/999888/deposit \
  -H "Content-Type: application/json" \
  -d '{
    "tx_hash": "实际的TRON交易哈希64字符",
    "amount": 50.0,
    "currency": "TRX"
  }'

# 期望响应: {"success":true,"message":"充值确认成功"}
```

#### 验证用户余额
```bash
# 查询用户余额
curl -X GET http://localhost:8002/api/users/999888/balance

# 期望响应: {"user_id":999888,"balance_trx":"50.000000","balance_usdt":"0.000000"}

# 查询余额变动记录
curl -X GET http://localhost:8002/api/users/999888/transactions
```

### 3.2 多用户充值测试

```bash
# 测试多个用户充值
for user_id in 111111 222222 333333; do
  curl -X POST http://localhost:8002/api/users/$user_id/deposit \
    -H "Content-Type: application/json" \
    -d '{
      "tx_hash": "不同的交易哈希'$user_id'0000000000000000000000000000000000000000",
      "amount": 20.0,
      "currency": "TRX"
    }'
  
  echo "User $user_id deposit completed"
  sleep 2
done
```

---

## 阶段4: 订单处理流程测试

### 4.1 创建测试订单

#### 单个订单测试
```bash
# 创建能量租赁订单
curl -X POST http://localhost:8002/api/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 999888,
    "energy_amount": 32000,
    "duration": "1h",
    "receive_address": "你的测试接收地址TR开头42字符"
  }'

# 记录返回的订单ID，例如: order_id="abc-123-def"
```

#### 订单状态跟踪
```bash
# 查询订单详情 (替换为实际订单ID)
curl -X GET http://localhost:8002/api/orders/abc-123-def

# 持续监控订单状态变化
watch -n 5 'curl -s http://localhost:8002/api/orders/abc-123-def | jq .status'

# 预期状态变化: pending → processing → completed (或 failed)
```

### 4.2 批量订单测试

```bash
# 创建多个订单测试并发处理能力
for i in {1..3}; do
  curl -X POST http://localhost:8002/api/orders/ \
    -H "Content-Type: application/json" \
    -d '{
      "user_id": '$(($i + 999888))',
      "energy_amount": 16000,
      "duration": "1h", 
      "receive_address": "接收地址TR开头42字符"
    }' &
done

wait
echo "All orders submitted"
```

### 4.3 订单取消测试

```bash
# 创建订单用于取消测试
order_response=$(curl -X POST http://localhost:8002/api/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 999888,
    "energy_amount": 8000,
    "duration": "1h",
    "receive_address": "接收地址"
  }')

# 提取订单ID
order_id=$(echo $order_response | jq -r '.id')

# 立即取消订单
curl -X POST http://localhost:8002/api/orders/$order_id/cancel

# 验证订单状态和退款
curl -X GET http://localhost:8002/api/orders/$order_id
curl -X GET http://localhost:8002/api/users/999888/balance
```

---

## 阶段5: Telegram Bot集成测试

### 5.1 Bot部署和配置

#### 启动Telegram Bot
```bash
# 在项目根目录
python3 main.py

# 或使用systemd服务
sudo tee /etc/systemd/system/trx-bot.service << EOF
[Unit]
Description=TRON Energy Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/trx-bot
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable trx-bot
sudo systemctl start trx-bot
```

### 5.2 端到端用户流程测试

#### 完整业务流程测试步骤

1. **用户注册和钱包管理**
   - 在Telegram中启动Bot
   - 添加接收Energy的钱包地址
   - 验证地址格式检查功能

2. **余额查询测试**
   - 使用"Address balance"功能
   - 验证显示真实的TRON网络余额
   - 测试多个不同地址的余额查询

3. **闪租页面测试**
   - 选择不同的能量数量 (32K, 65K等)
   - 选择不同的租用时长 (1h, 1d等)
   - 验证费用计算的准确性

4. **模拟充值流程**
   - 通过API为测试用户充值
   - 在Bot中验证余额更新

5. **完整下单流程**
   - 选择能量和时长
   - 确认订单详情
   - 点击"Buy"按钮
   - 观察订单处理过程

6. **订单状态跟踪**
   - 查看订单处理状态
   - 验证Energy是否成功委托
   - 检查用户余额扣减

---

## 阶段6: 性能和稳定性测试

### 6.1 压力测试

#### API性能测试
```bash
# 安装测试工具
apt install -y apache2-utils

# API响应时间测试
ab -n 100 -c 10 http://localhost:8002/health

# 用户余额查询压力测试  
ab -n 50 -c 5 http://localhost:8002/api/users/12345/balance
```

#### 并发订单测试
```bash
#!/bin/bash
# 创建并发订单测试脚本 concurrent_orders.sh

for i in {1..10}; do
  {
    curl -X POST http://localhost:8002/api/orders/ \
      -H "Content-Type: application/json" \
      -d '{
        "user_id": '$((1000 + $i))',
        "energy_amount": 16000,
        "duration": "1h",
        "receive_address": "TTestAddress1234567890123456789012"
      }'
    echo "Order $i completed"
  } &
done

wait
echo "All concurrent orders submitted"
```

### 6.2 长时间稳定性测试

#### 24小时运行测试
```bash
# 创建监控脚本 monitor.sh
#!/bin/bash
while true; do
  # 检查API健康状态
  status=$(curl -s http://localhost:8002/health | jq -r '.status')
  echo "$(date): API Status - $status"
  
  # 检查数据库连接
  db_test=$(curl -s http://localhost:8002/api/users/12345/balance)
  echo "$(date): DB Connection - OK"
  
  # 检查服务进程
  if ! pgrep -f "python3 main.py" > /dev/null; then
    echo "$(date): WARNING - Backend service not running!"
  fi
  
  sleep 300  # 每5分钟检查一次
done
```

---

## 阶段7: 安全性测试

### 7.1 私钥安全验证

```bash
# 检查私钥是否正确加密存储
python3 << EOF
from backend.app.services.tron_service import TronTransactionService
from backend.app.database import SessionLocal

db = SessionLocal()
service = TronTransactionService(db)

# 测试加密/解密功能
test_key = "0123456789abcdef" * 4  # 64字符测试私钥
encrypted = service.encrypt_private_key(test_key)
decrypted = service.decrypt_private_key(encrypted)

print(f"Original:  {test_key}")
print(f"Encrypted: {encrypted}")
print(f"Decrypted: {decrypted}")
print(f"Match: {test_key == decrypted}")
EOF
```

### 7.2 API安全测试

```bash
# 测试无效数据处理
curl -X POST http://localhost:8002/api/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "invalid",
    "energy_amount": -1000,
    "duration": "invalid_duration",
    "receive_address": "invalid_address"
  }'

# 应该返回适当的错误信息，不应该崩溃
```

---

## 监控和日志

### 实时监控设置

#### 日志监控
```bash
# 查看API服务日志
tail -f /var/log/trx-backend.log

# 查看Telegram Bot日志  
tail -f /var/log/trx-bot.log

# 查看系统资源使用
top -p $(pgrep -f "python3 main.py")
```

#### 关键指标监控
```bash
# 创建简单监控脚本
#!/bin/bash
# monitor_metrics.sh

echo "=== TRON Energy Helper Metrics ==="
echo "Time: $(date)"
echo

# API响应时间
echo "API Response Time:"
time curl -s http://localhost:8002/health > /dev/null

# 数据库订单统计
echo -e "\nOrder Statistics:"
curl -s http://localhost:8002/api/orders?limit=1000 | jq '. | length'

# 钱包池状态
echo -e "\nWallet Pool Status:"
curl -s http://localhost:8002/api/supplier-wallets/ | jq '.[] | {address: .wallet_address, trx: .trx_balance, energy: .energy_available}'

echo "=========================="
```

---

## 测试验收标准

### 必须通过的测试

#### 功能测试 ✅
- [ ] 所有API端点正常响应
- [ ] 用户充值和余额管理正常
- [ ] 供应商钱包添加和管理正常
- [ ] 订单创建和处理流程完整
- [ ] Telegram Bot所有功能正常

#### 性能测试 ✅
- [ ] API平均响应时间 < 2秒
- [ ] 支持至少10个并发订单处理
- [ ] 系统连续运行24小时无异常
- [ ] 内存使用稳定，无明显泄露

#### 安全测试 ✅
- [ ] 私钥正确加密存储
- [ ] 无效输入正确处理，不崩溃
- [ ] 敏感信息不在日志中泄露
- [ ] 数据库连接安全

#### 业务流程测试 ✅
- [ ] 真实TRON交易成功执行
- [ ] 订单状态正确跟踪
- [ ] 失败订单正确退款
- [ ] 用户余额准确更新

---

## 问题排查指南

### 常见问题和解决方案

#### 1. API服务无法启动
```bash
# 检查端口占用
netstat -tlnp | grep 8002

# 检查依赖安装
pip3 install -r backend/requirements.txt

# 检查环境变量
cat backend/.env
```

#### 2. 数据库连接失败
```bash
# 检查PostgreSQL服务状态
systemctl status postgresql

# 测试数据库连接
psql -h localhost -U trx_user -d trx_energy
```

#### 3. TRON网络连接问题
```bash
# 测试TRON网络连通性
python3 -c "from tronpy import Tron; t=Tron(); print('Latest block:', t.get_latest_block_number())"
```

#### 4. 订单处理失败
```bash
# 检查Celery Worker状态
ps aux | grep celery

# 检查Redis连接
redis-cli ping

# 查看任务队列状态
python3 -c "
import redis
r = redis.Redis()
print('Pending tasks:', r.llen('celery'))
"
```

---

## 测试完成后的清理

### 安全清理步骤

1. **更换所有测试私钥**
   - 立即生成新的供应商钱包
   - 转移测试钱包中的剩余资金

2. **清理测试数据**
   ```bash
   # 清空测试订单 (可选)
   psql -h localhost -U trx_user -d trx_energy << EOF
   DELETE FROM orders WHERE created_at < NOW();
   DELETE FROM balance_transactions WHERE created_at < NOW();
   EOF
   ```

3. **更新生产配置**
   - 更换所有密钥和Token
   - 设置合适的环境变量
   - 配置生产域名和HTTPS

---

## 总结

通过以上完整的测试流程，你可以确保TRON能量助手系统在生产环境中稳定可靠地运行。测试完成后，系统即可投入实际业务使用。

记住始终遵循安全最佳实践，定期备份数据，并持续监控系统运行状况。

---

**最后更新**: 2025-08-24  
**适用版本**: v2.2 - TRON交易引擎集成  
**预计测试时间**: 2-3天完整测试