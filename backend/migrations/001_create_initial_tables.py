"""create initial tables

Revision ID: 001
Revises: 
Create Date: 2025-08-23

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # 创建用户表
    op.create_table('users',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column('last_name', sa.String(length=255), nullable=True),
        sa.Column('balance_trx', sa.DECIMAL(precision=18, scale=6), server_default='0', nullable=True),
        sa.Column('balance_usdt', sa.DECIMAL(precision=18, scale=6), server_default='0', nullable=True),
        sa.Column('total_orders', sa.Integer(), server_default='0', nullable=True),
        sa.Column('total_spent', sa.DECIMAL(precision=18, scale=6), server_default='0', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建用户钱包表
    op.create_table('user_wallets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=True),
        sa.Column('wallet_address', sa.String(length=42), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建订单表
    op.create_table('orders',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=True),
        sa.Column('receive_address', sa.String(length=42), nullable=False),
        sa.Column('energy_amount', sa.Integer(), nullable=False),
        sa.Column('duration_hours', sa.Integer(), nullable=False),
        sa.Column('cost_trx', sa.DECIMAL(precision=18, scale=6), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='pending', nullable=True),
        sa.Column('supplier_wallet', sa.String(length=42), nullable=True),
        sa.Column('tx_hash', sa.String(length=66), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), server_default='0', nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建余额变动表
    op.create_table('balance_transactions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=True),
        sa.Column('transaction_type', sa.String(length=20), nullable=False),
        sa.Column('amount', sa.DECIMAL(precision=18, scale=6), nullable=False),
        sa.Column('balance_after', sa.DECIMAL(precision=18, scale=6), nullable=False),
        sa.Column('reference_id', sa.String(length=255), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建供应商钱包表
    op.create_table('supplier_wallets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('wallet_address', sa.String(length=42), nullable=False),
        sa.Column('private_key_encrypted', sa.Text(), nullable=False),
        sa.Column('trx_balance', sa.DECIMAL(precision=18, scale=6), server_default='0', nullable=True),
        sa.Column('energy_available', sa.Integer(), server_default='0', nullable=True),
        sa.Column('energy_limit', sa.Integer(), server_default='0', nullable=True),
        sa.Column('bandwidth_available', sa.Integer(), server_default='0', nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=True),
        sa.Column('last_balance_check', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('wallet_address')
    )
    
    # 创建索引
    op.create_index('idx_orders_user_id', 'orders', ['user_id'])
    op.create_index('idx_orders_status', 'orders', ['status'])
    op.create_index('idx_orders_created_at', 'orders', ['created_at'])
    op.create_index('idx_user_wallets_user_id', 'user_wallets', ['user_id'])
    op.create_index('idx_balance_transactions_user_id', 'balance_transactions', ['user_id'])

def downgrade():
    op.drop_index('idx_balance_transactions_user_id')
    op.drop_index('idx_user_wallets_user_id')
    op.drop_index('idx_orders_created_at')
    op.drop_index('idx_orders_status')
    op.drop_index('idx_orders_user_id')
    op.drop_table('supplier_wallets')
    op.drop_table('balance_transactions')
    op.drop_table('orders')
    op.drop_table('user_wallets')
    op.drop_table('users')