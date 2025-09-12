# 后台管理系统API接口设计

## 1. 订单管理API

### 创建订单
```
POST /api/orders
{
  "user_id": "telegram_user_id",
  "energy_amount": 65000,
  "duration": "1h", 
  "receive_address": "TQ5kjKLLm9X4L2D1JgogNis6V1YoAm6sv2",
  "cost_trx": 5.85
}
```

### 查询订单状态
```
GET /api/orders/{order_id}
POST /api/orders/status
{
  "user_id": "telegram_user_id",
  "order_ids": ["order_1", "order_2"]
}
```

### 订单列表
```
GET /api/orders?user_id={user_id}&status={status}&page={page}
```

## 2. 用户管理API

### 用户余额查询
```
GET /api/users/{user_id}/balance
```

### 用户余额充值确认
```
POST /api/users/{user_id}/deposit
{
  "tx_hash": "0x123...",
  "amount": 10.0,
  "currency": "TRX"
}
```

### 用户余额扣减（下单时）
```
POST /api/users/{user_id}/deduct
{
  "amount": 5.85,
  "order_id": "order_123",
  "reason": "energy_purchase"
}
```

## 3. 供应商钱包管理API

### 钱包池状态
```
GET /api/wallet-pool/status
```

### 检查钱包库存
```
POST /api/wallet-pool/check-availability
{
  "energy_amount": 65000,
  "duration": "1h"
}
```

### 执行能量委托
```
POST /api/wallet-pool/delegate-energy
{
  "from_address": "supplier_wallet",
  "to_address": "user_wallet", 
  "energy_amount": 65000,
  "duration_hours": 1
}
```

## 4. 财务管理API

### 收入统计
```
GET /api/finance/revenue?period=daily&start_date=2023-01-01
```

### 成本分析
```
GET /api/finance/costs?period=monthly
```

### 价格策略查询
```
GET /api/finance/pricing?energy_amount=65000&duration=1h
```

## 5. 监控API

### 系统健康检查
```
GET /api/monitor/health
```

### 钱包余额监控
```
GET /api/monitor/wallet-balances
```

### 订单处理队列状态
```
GET /api/monitor/order-queue
```

## 6. 配置管理API

### 价格配置
```
GET /PUT /api/config/pricing
{
  "base_price_per_energy": 0.00001,
  "duration_multipliers": {
    "1h": 0.8,
    "1d": 1.0,
    "3d": 2.5
  }
}
```

### 系统参数
```
GET /PUT /api/config/system
{
  "max_energy_per_order": 10000000,
  "min_energy_per_order": 1000,
  "auto_refund_enabled": true
}
```