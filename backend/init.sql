-- 初始化数据库表结构
-- 此文件在Docker Compose启动时自动执行

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    balance_trx DECIMAL(18,6) DEFAULT 0,
    balance_usdt DECIMAL(18,6) DEFAULT 0,
    total_orders INTEGER DEFAULT 0,
    total_spent DECIMAL(18,6) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建用户钱包表
CREATE TABLE IF NOT EXISTS user_wallets (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    wallet_address VARCHAR(42) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, wallet_address)
);

-- 创建订单表
CREATE TABLE IF NOT EXISTS orders (
    id VARCHAR(36) PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    receive_address VARCHAR(42) NOT NULL,
    energy_amount INTEGER NOT NULL,
    duration_hours INTEGER NOT NULL,
    cost_trx DECIMAL(18,6) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    supplier_wallet VARCHAR(42),
    tx_hash VARCHAR(66),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- 创建余额变动表
CREATE TABLE IF NOT EXISTS balance_transactions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    transaction_type VARCHAR(20) NOT NULL,
    amount DECIMAL(18,6) NOT NULL,
    balance_after DECIMAL(18,6) NOT NULL,
    reference_id VARCHAR(255),
    description VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建供应商钱包表
CREATE TABLE IF NOT EXISTS supplier_wallets (
    id SERIAL PRIMARY KEY,
    wallet_address VARCHAR(42) UNIQUE NOT NULL,
    private_key_encrypted TEXT NOT NULL,
    trx_balance DECIMAL(18,6) DEFAULT 0,
    energy_available INTEGER DEFAULT 0,
    energy_limit INTEGER DEFAULT 0,
    bandwidth_available INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    last_balance_check TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_user_wallets_user_id ON user_wallets(user_id);
CREATE INDEX IF NOT EXISTS idx_balance_transactions_user_id ON balance_transactions(user_id);

-- 插入测试数据 (可选)
INSERT INTO users (id, username, first_name, balance_trx) 
VALUES (123456, 'testuser', 'Test User', 100.000000)
ON CONFLICT (id) DO NOTHING;

-- 输出成功信息
SELECT 'Database initialization completed successfully' AS status;