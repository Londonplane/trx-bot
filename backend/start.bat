@echo off
REM 后端服务快速启动脚本 (Windows版本)

echo 🚀 启动TRON能量助手后端服务...

REM 检查是否在backend目录
if not exist "main.py" (
    echo ❌ 请在backend目录下运行此脚本
    pause
    exit /b 1
)

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装，请先安装Python3.8+
    pause
    exit /b 1
)

REM 检查是否有虚拟环境
if not exist "venv" (
    echo 📦 创建Python虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 🔧 激活虚拟环境...
call venv\Scripts\activate

REM 安装依赖
echo 📚 安装依赖包...
pip install -r requirements.txt

REM 检查环境变量文件
if not exist ".env" (
    echo ⚙️ 复制环境变量配置...
    copy .env.example .env
    echo 📝 请编辑.env文件配置数据库连接信息
)

REM 启动服务
echo 🌟 启动后端API服务...
echo 📍 API文档地址: http://localhost:8000/docs
echo 🔍 健康检查: http://localhost:8000/health
echo.
echo 按Ctrl+C停止服务
echo ==========================
echo.

python main.py