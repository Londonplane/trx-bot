from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import orders, users, wallets, supplier_wallets
from app.database import engine, Base
import logging
import os

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TRON Energy Backend API",
    description="TRON能量助手后台管理系统API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(wallets.router, prefix="/api/wallets", tags=["wallets"])
app.include_router(supplier_wallets.router, prefix="/api/supplier-wallets", tags=["supplier-wallets"])

@app.get("/")
async def root():
    return {
        "message": "TRON Energy Backend API", 
        "version": "1.0.0",
        "admin": "Visit /admin for management interface"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API服务正常运行"}

# 挂载静态文件（管理后台）- 放在最后以避免路由冲突
admin_path = os.path.join(os.path.dirname(__file__), "admin")
print(f"Admin path: {admin_path}")
print(f"Admin path exists: {os.path.exists(admin_path)}")
if os.path.exists(admin_path):
    app.mount("/admin", StaticFiles(directory=admin_path, html=True), name="admin")
    print("Admin static files mounted successfully")
else:
    print("Admin directory not found!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)