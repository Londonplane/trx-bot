@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"

echo ====================================================
echo               TRON Bot 快速启动器
echo ====================================================
echo.

echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或不在PATH中
    echo 请先安装Python 3.7+
    pause
    exit /b 1
)

echo ✅ Python环境检查通过
echo.

echo 正在启动Bot...
echo 提示: 按 Ctrl+C 可停止Bot
echo ====================================================
python main.py

echo.
echo ====================================================
echo Bot已停止
echo ====================================================
pause