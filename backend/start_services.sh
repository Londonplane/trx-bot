#!/bin/bash

# TRON能量助手后端服务启动脚本

echo "启动TRON能量助手后端服务..."

# 检查Python环境
if ! command -v python &> /dev/null; then
    echo "错误: Python未安装或不在PATH中"
    exit 1
fi

# 检查依赖
echo "检查Python依赖..."
python -c "import fastapi, sqlalchemy, tronpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "安装Python依赖..."
    pip install -r requirements.txt
fi

# 设置环境变量
export DATABASE_URL="${DATABASE_URL:-sqlite:///./trx_energy.db}"
export REDIS_URL="${REDIS_URL:-redis://localhost:6379}"
export SECRET_KEY="${SECRET_KEY:-development-key-change-in-production}"

echo "数据库URL: $DATABASE_URL"
echo "Redis URL: $REDIS_URL"

# 启动FastAPI服务器
echo "启动FastAPI服务器..."
python main.py &
API_PID=$!

# 检查Redis是否可用
echo "检查Redis连接..."
python -c "import redis; r=redis.from_url('$REDIS_URL'); r.ping()" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "Redis连接正常，启动Celery Worker..."
    celery -A tron_worker worker --loglevel=info &
    WORKER_PID=$!
    
    echo "启动Celery Beat（定时任务）..."
    celery -A tron_worker beat --loglevel=info &
    BEAT_PID=$!
else
    echo "警告: Redis不可用，跳过Celery服务启动"
    echo "订单处理将需要手动触发"
fi

echo ""
echo "========================================"
echo "TRON能量助手后端服务已启动"
echo "========================================"
echo "API服务: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo "健康检查: http://localhost:8000/health"
echo ""

# 显示进程信息
echo "运行中的进程:"
echo "FastAPI (PID: $API_PID)"
if [ ! -z "$WORKER_PID" ]; then
    echo "Celery Worker (PID: $WORKER_PID)"
fi
if [ ! -z "$BEAT_PID" ]; then
    echo "Celery Beat (PID: $BEAT_PID)"
fi

echo ""
echo "按 Ctrl+C 停止所有服务"

# 捕获中断信号，优雅关闭
trap 'echo "正在关闭服务..."; kill $API_PID 2>/dev/null; kill $WORKER_PID 2>/dev/null; kill $BEAT_PID 2>/dev/null; exit 0' INT

# 等待进程结束
wait