#!/bin/bash
# 后端服务快速启动脚本

echo "🚀 启动TRON能量助手后端服务..."

# 检查是否在backend目录
if [ ! -f "main.py" ]; then
    echo "❌ 请在backend目录下运行此脚本"
    exit 1
fi

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装，请先安装Python3.8+"
    exit 1
fi

# 检查是否有虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate 2>/dev/null || venv\Scripts\activate

# 安装依赖
echo "📚 安装依赖包..."
pip install -r requirements.txt

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "⚙️ 复制环境变量配置..."
    cp .env.example .env
    echo "📝 请编辑.env文件配置数据库连接信息"
fi

# 启动服务
echo "🌟 启动后端API服务..."
echo "📍 API文档地址: http://localhost:8000/docs"
echo "🔍 健康检查: http://localhost:8000/health"
echo ""
echo "按Ctrl+C停止服务"
echo "=========================="

python main.py