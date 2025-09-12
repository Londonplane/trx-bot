# 闪租页能量购买完整API调用流程

## 概述

本文档详细记录了用户在闪租页购买能量的完整过程中涉及的所有API调用序列，包括前端交互、后端处理和TRON区块链操作。

---

## 完整购买流程的API调用序列

### 1. 用户钱包管理阶段

#### 1.1 获取用户钱包列表
```http
GET /api/wallets/users/{user_id}
```

**调用时机**：用户点击"Select address"按钮时

**功能**：
- 获取用户已绑定的钱包地址列表
- 用于显示钱包选择界面

**响应示例**：
```json
{
  "wallets": [
    {
      "id": 1,
      "wallet_address": "TQ5kjKLLm9X4L2D1JgogNis6V1YoAm6sv2",
      "created_at": "2023-08-23T10:00:00Z"
    }
  ]
}
```

#### 1.2 添加新钱包地址
```http
POST /api/wallets/users/{user_id}
```

**调用时机**：用户输入新的TRON地址并确认添加时

**请求体**：
```json
{
  "wallet_address": "TQ5kjKLLm9X4L2D1JgogNis6V1YoAm6sv2"
}
```

**功能**：
- 验证TRON地址格式的有效性
- 存储到用户钱包列表中
- 防止重复添加

---

### 2. 余额查询阶段

#### 2.1 系统余额查询（支付余额）
```http
GET /api/users/{user_id}/balance
```

**调用时机**：用户进入闪租页面或需要确认支付能力时

**功能**：
- 获取用户在系统中的TRX余额（用于支付订单费用）
- 确认用户是否有足够余额支付订单

**响应示例**：
```json
{
  "user_id": 123456789,
  "balance_trx": 25.500000,
  "last_updated": "2023-08-23T12:00:00Z"
}
```

#### 2.2 钱包余额查询（TRON链上余额）
```http
外部API: https://apilist.tronscan.org/api/account?address={address}
```

**调用时机**：用户点击"Address balance"按钮时

**功能**：
- 查询指定钱包地址在TRON链上的实时余额
- 显示TRX余额、Energy可用量、Bandwidth可用量
- 帮助用户了解接收地址的当前状态

**注意**：此API调用仍使用现有的TRON API实现，不经过后端系统

---

### 3. 订单创建阶段

#### 3.1 创建能量租赁订单
```http
POST /api/orders
```

**调用时机**：用户选择完参数并点击"Buy"按钮时

**请求体**：
```json
{
  "user_id": "123456789",
  "energy_amount": 65000,
  "duration": "1h", 
  "receive_address": "TQ5kjKLLm9X4L2D1JgogNis6V1YoAm6sv2",
  "cost_trx": 5.85
}
```

**功能**：
- 创建新的能量租赁订单
- 生成唯一订单ID
- 初始状态为"pending"

**响应示例**：
```json
{
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "created_at": "2023-08-23T14:00:00Z",
  "estimated_completion": "2023-08-23T14:05:00Z"
}
```

---

### 4. 支付处理阶段

#### 4.1 用户余额扣减
```http
POST /api/users/{user_id}/deduct
```

**调用时机**：订单创建成功后自动触发

**请求体**：
```json
{
  "amount": 5.85,
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "reason": "energy_purchase"
}
```

**功能**：
- 从用户系统余额中扣除订单费用
- 记录余额变动日志
- 确保支付的原子性操作

---

### 5. 后端业务处理（内部API调用）

#### 5.1 检查供应商钱包可用性
```http
POST /api/wallet-pool/check-availability
```

**调用时机**：订单创建后，后端内部自动调用

**请求体**：
```json
{
  "energy_amount": 65000,
  "duration": "1h"
}
```

**功能**：
- 检查钱包池中是否有足够的Energy库存
- 选择最优的供应商钱包执行委托

**响应示例**：
```json
{
  "available": true,
  "selected_wallet": "TVj7RNVHNv1ym6JxWePCHnKgdvnGqr4f2S",
  "available_energy": 150000
}
```

---

### 6. 区块链交易执行阶段（阶段2功能）

#### 6.1 执行能量委托交易
```http
POST /api/wallet-pool/delegate-energy
```

**调用时机**：确认有可用钱包后自动执行

**请求体**：
```json
{
  "from_address": "TVj7RNVHNv1ym6JxWePCHnKgdvnGqr4f2S",
  "to_address": "TQ5kjKLLm9X4L2D1JgogNis6V1YoAm6sv2", 
  "energy_amount": 65000,
  "duration_hours": 1
}
```

**功能**：
- 调用TRON智能合约的`delegateResource`方法
- 执行实际的能量委托交易
- 监控交易广播和确认状态

**响应示例**：
```json
{
  "transaction_hash": "0x1234567890abcdef...",
  "status": "broadcasted",
  "estimated_confirmation": "2023-08-23T14:03:00Z"
}
```

---

### 7. 订单状态跟踪

#### 7.1 查询订单状态
```http
GET /api/orders/{order_id}
```

**调用时机**：
- 用户主动查询订单进度
- 前端定期轮询更新状态

**响应示例**：
```json
{
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "user_id": "123456789",
  "energy_amount": 65000,
  "duration": "1h",
  "receive_address": "TQ5kjKLLm9X4L2D1JgogNis6V1YoAm6sv2",
  "cost_trx": 5.85,
  "transaction_hash": "0x1234567890abcdef...",
  "created_at": "2023-08-23T14:00:00Z",
  "completed_at": "2023-08-23T14:03:00Z"
}
```

#### 7.2 订单状态流转
```
pending → processing → completed
              ↓
           failed → refunded
```

---

## 错误处理和异常情况

### 余额不足处理
```http
POST /api/orders
```
**错误响应**：
```json
{
  "error": "insufficient_balance",
  "message": "用户余额不足，当前余额: 3.50 TRX，需要: 5.85 TRX",
  "required_amount": 5.85,
  "current_balance": 3.50
}
```

### 钱包库存不足处理
**内部处理**：
- 订单状态标记为"failed"
- 自动触发退款流程
- 通知用户订单失败原因

### API调用失败降级机制
- **网络异常**：重试机制，最多3次
- **后端不可用**：降级到本地存储模式
- **TRON网络异常**：切换到备用API节点

---

## 当前实现状态

### ✅ 阶段1已完成（v2.1）
- API调用 1-4：钱包管理、余额查询、订单创建、支付扣减
- 后端数据库存储和API接口
- Bot前端集成和降级机制

### 🔄 阶段2开发中
- API调用 5-6：供应商钱包管理、区块链交易执行
- 真实的TRON能量委托功能
- 交易状态监控和确认

### 📋 阶段3计划中
- 完善的监控和报警系统
- 运营管理后台界面
- 高可用性和容错机制

---

## 技术架构特点

### 混合架构设计
- **系统数据**：订单、用户、钱包管理 → 后端API
- **区块链数据**：链上余额查询 → TRON API
- **业务逻辑**：支付、委托执行 → 后端API + 区块链交互

### 渐进式升级策略
1. **Mock数据** → **后端API** → **区块链集成**
2. 每个阶段都保持功能完整性
3. 降级机制确保系统可用性

### 用户体验优化
- 所有API调用对用户透明
- 消息编辑保持界面连续性
- 实时状态更新和进度提示
- 错误情况的友好提示

---

## 开发和测试建议

### API调用测试
```bash
# 测试完整购买流程
python test_api.py --test-purchase-flow

# 测试单个API接口
curl -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{"user_id": "123", "energy_amount": 65000, "duration": "1h", "receive_address": "TQ5kjKLLm9X4L2D1JgogNis6V1YoAm6sv2", "cost_trx": 5.85}'
```

### 监控要点
- API响应时间（目标 < 500ms）
- 订单成功率（目标 > 95%）
- 支付处理准确性（100%）
- 区块链交易确认率（目标 > 90%）

这个完整的API调用流程确保了闪租页从用户交互到订单完成的全流程数字化管理，为后续的商业化运营奠定了坚实的技术基础。