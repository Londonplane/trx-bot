from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import orders, users, wallets
from app.database import engine, Base
import logging

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

# 注册路由
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(wallets.router, prefix="/api/wallets", tags=["wallets"])

@app.get("/")
async def root():
    return {"message": "TRON Energy Backend API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API服务正常运行"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)