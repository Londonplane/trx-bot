from sqlalchemy.orm import Session
from app.models import UserWallet, User
from app.schemas import UserWalletResponse
import logging

logger = logging.getLogger(__name__)

class WalletService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_wallets(self, user_id: int) -> list[UserWalletResponse]:
        """获取用户钱包地址列表"""
        wallets = self.db.query(UserWallet).filter(
            UserWallet.user_id == user_id,
            UserWallet.is_active == True
        ).order_by(UserWallet.created_at.desc()).all()
        
        return [self._wallet_to_response(wallet) for wallet in wallets]
    
    def add_user_wallet(self, user_id: int, wallet_address: str) -> bool:
        """添加用户钱包地址"""
        # 验证TRON地址格式
        if not self._is_valid_tron_address(wallet_address):
            raise ValueError("无效的TRON地址格式")
        
        # 检查是否已存在
        existing_wallet = self.db.query(UserWallet).filter(
            UserWallet.user_id == user_id,
            UserWallet.wallet_address == wallet_address
        ).first()
        
        if existing_wallet:
            return False  # 地址已存在
        
        # 确保用户存在
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(id=user_id)
            self.db.add(user)
            self.db.flush()
        
        # 添加钱包地址
        wallet = UserWallet(
            user_id=user_id,
            wallet_address=wallet_address
        )
        
        self.db.add(wallet)
        self.db.commit()
        
        logger.info(f"用户 {user_id} 添加钱包地址: {wallet_address}")
        return True
    
    def remove_user_wallet(self, user_id: int, wallet_address: str) -> bool:
        """删除用户钱包地址"""
        wallet = self.db.query(UserWallet).filter(
            UserWallet.user_id == user_id,
            UserWallet.wallet_address == wallet_address
        ).first()
        
        if not wallet:
            return False
        
        # 软删除：设置为不活跃
        wallet.is_active = False
        self.db.commit()
        
        logger.info(f"用户 {user_id} 删除钱包地址: {wallet_address}")
        return True
    
    def _is_valid_tron_address(self, address: str) -> bool:
        """验证TRON地址格式"""
        if not address:
            return False
        
        # 基本格式检查
        if address.startswith('T') and len(address) == 34:
            return True
        elif len(address) == 42 and address.startswith('41'):
            return True
        
        return False
    
    def _wallet_to_response(self, wallet: UserWallet) -> UserWalletResponse:
        """转换钱包模型为响应格式"""
        return UserWalletResponse(
            id=wallet.id,
            wallet_address=wallet.wallet_address,
            is_active=wallet.is_active,
            created_at=wallet.created_at
        )