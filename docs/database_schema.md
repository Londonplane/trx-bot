# 数据库Schema设计

## 1. 用户管理

### users - 用户基本信息
```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY,  -- Telegram用户ID
    username VARCHAR(255),  -- Telegram用户名
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    balance_trx DECIMAL(18,6) DEFAULT 0,  -- TRX余额
    balance_usdt DECIMAL(18,6) DEFAULT 0, -- USDT余额
    total_orders INTEGER DEFAULT 0,        -- 总订单数
    total_spent DECIMAL(18,6) DEFAULT 0,   -- 总消费金额
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### user_wallets - 用户钱包地址
```sql
CREATE TABLE user_wallets (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    wallet_address VARCHAR(42) NOT NULL,  -- TRON地址
    is_active BOOLEAN DEFAULT true,       -- 是否启用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, wallet_address)
);
```

## 2. 订单系统

### orders - 能量租赁订单
```sql
CREATE TABLE orders (
    id VARCHAR(36) PRIMARY KEY,           -- UUID
    user_id BIGINT REFERENCES users(id),
    receive_address VARCHAR(42) NOT NULL, -- 接收能量的地址
    energy_amount INTEGER NOT NULL,       -- 能量数量
    duration_hours INTEGER NOT NULL,      -- 租期（小时）
    cost_trx DECIMAL(18,6) NOT NULL,     -- 费用
    status VARCHAR(20) DEFAULT 'pending', -- pending/processing/completed/failed/cancelled
    supplier_wallet VARCHAR(42),          -- 供应商钱包地址
    tx_hash VARCHAR(66),                  -- 交易哈希
    error_message TEXT,                   -- 错误信息
    retry_count INTEGER DEFAULT 0,       -- 重试次数
    expires_at TIMESTAMP,                 -- 订单过期时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
```

## 3. 供应商钱包池

### supplier_wallets - 供应商钱包池
```sql
CREATE TABLE supplier_wallets (
    id SERIAL PRIMARY KEY,
    wallet_address VARCHAR(42) UNIQUE NOT NULL,
    private_key_encrypted TEXT NOT NULL,  -- 加密存储的私钥
    trx_balance DECIMAL(18,6) DEFAULT 0,
    energy_available INTEGER DEFAULT 0,   -- 可委托的Energy
    energy_limit INTEGER DEFAULT 0,       -- Energy总限制
    bandwidth_available INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,       -- 是否启用
    last_balance_check TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### energy_delegations - Energy委托记录
```sql
CREATE TABLE energy_delegations (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(36) REFERENCES orders(id),
    from_wallet VARCHAR(42) REFERENCES supplier_wallets(wallet_address),
    to_wallet VARCHAR(42) NOT NULL,
    energy_amount INTEGER NOT NULL,
    duration_hours INTEGER NOT NULL,
    tx_hash VARCHAR(66),
    status VARCHAR(20) DEFAULT 'pending', -- pending/confirmed/expired
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 4. 财务管理

### deposits - 充值记录
```sql
CREATE TABLE deposits (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    tx_hash VARCHAR(66) UNIQUE NOT NULL,
    amount DECIMAL(18,6) NOT NULL,
    currency VARCHAR(10) NOT NULL,        -- TRX/USDT
    equivalent_trx DECIMAL(18,6) NOT NULL, -- 等值TRX金额
    status VARCHAR(20) DEFAULT 'pending', -- pending/confirmed/failed
    block_height BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP
);
```

### balance_transactions - 余额变动记录
```sql
CREATE TABLE balance_transactions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    transaction_type VARCHAR(20) NOT NULL, -- deposit/deduct/refund
    amount DECIMAL(18,6) NOT NULL,
    balance_after DECIMAL(18,6) NOT NULL,
    reference_id VARCHAR(255),            -- 关联订单ID或充值ID
    description VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 5. 系统配置

### system_config - 系统配置
```sql
CREATE TABLE system_config (
    key VARCHAR(255) PRIMARY KEY,
    value TEXT NOT NULL,
    data_type VARCHAR(20) DEFAULT 'string', -- string/number/boolean/json
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### pricing_rules - 价格规则
```sql
CREATE TABLE pricing_rules (
    id SERIAL PRIMARY KEY,
    energy_min INTEGER NOT NULL,
    energy_max INTEGER NOT NULL,
    duration_hours INTEGER NOT NULL,
    base_price_per_energy DECIMAL(10,8) NOT NULL,
    time_multiplier DECIMAL(4,2) DEFAULT 1.0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 6. 监控日志

### monitor_logs - 系统监控日志
```sql
CREATE TABLE monitor_logs (
    id SERIAL PRIMARY KEY,
    log_type VARCHAR(50) NOT NULL,        -- wallet_balance/api_error/order_timeout等
    wallet_address VARCHAR(42),
    message TEXT,
    severity VARCHAR(20) DEFAULT 'info',  -- info/warning/error/critical
    metadata JSON,                        -- 额外的监控数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 索引设计

```sql
-- 订单相关索引
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- 用户钱包索引
CREATE INDEX idx_user_wallets_user_id ON user_wallets(user_id);

-- 充值记录索引
CREATE INDEX idx_deposits_user_id ON deposits(user_id);
CREATE INDEX idx_deposits_tx_hash ON deposits(tx_hash);

-- 余额变动索引
CREATE INDEX idx_balance_transactions_user_id ON balance_transactions(user_id);

-- 监控日志索引
CREATE INDEX idx_monitor_logs_type_time ON monitor_logs(log_type, created_at);
```

## 数据存储方案建议

### 主数据库：PostgreSQL
- 支持复杂查询和事务
- JSON字段支持灵活配置存储
- 高并发性能良好

### 缓存层：Redis
- 用户会话状态缓存
- 钱包余额缓存
- 订单处理队列

### 文件存储
- 钱包私钥加密文件
- 系统日志文件
- 备份文件