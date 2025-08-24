@echo off
setlocal

REM TRON能量助手后端服务启动脚本 (Windows版本)

echo 启动TRON能量助手后端服务...

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Python未安装或不在PATH中
    exit /b 1
)

REM 检查依赖
echo 检查Python依赖...
python -c "import fastapi, sqlalchemy, tronpy" >nul 2>&1
if errorlevel 1 (
    echo 安装Python依赖...
    pip install -r requirements.txt
)

REM 设置环境变量
if "%DATABASE_URL%"=="" set DATABASE_URL=sqlite:///./trx_energy.db
if "%REDIS_URL%"=="" set REDIS_URL=redis://localhost:6379
if "%SECRET_KEY%"=="" set SECRET_KEY=development-key-change-in-production

echo 数据库URL: %DATABASE_URL%
echo Redis URL: %REDIS_URL%

REM 启动FastAPI服务器
echo 启动FastAPI服务器...
start /B python main.py

REM 检查Redis是否可用
echo 检查Redis连接...
python -c "import redis; r=redis.from_url('%REDIS_URL%'); r.ping()" >nul 2>&1
if not errorlevel 1 (
    echo Redis连接正常，启动Celery Worker...
    start /B celery -A tron_worker worker --loglevel=info
    
    echo 启动Celery Beat（定时任务）...
    start /B celery -A tron_worker beat --loglevel=info
) else (
    echo 警告: Redis不可用，跳过Celery服务启动
    echo 订单处理将需要手动触发
)

echo.
echo ========================================
echo TRON能量助手后端服务已启动
echo ========================================
echo API服务: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo 健康检查: http://localhost:8000/health
echo.
echo 按任意键停止服务...
pause >nul

REM 停止所有Python进程 (简单方式，生产环境需要更精确的进程管理)
taskkill /F /IM python.exe >nul 2>&1