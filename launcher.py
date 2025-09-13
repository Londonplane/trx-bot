#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TRON 能量助手 - 生产级启动器
一劳永逸解决进程管理和编码问题
"""

import os
import sys
import time
import signal
import subprocess
import threading
import locale
from pathlib import Path
import requests

# 设置全局编码环境
if sys.platform == "win32":
    # Windows 编码修复
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONLEGACYWINDOWSSTDIO'] = '1'
    
    # 设置控制台编码
    try:
        # 尝试设置控制台为 UTF-8
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleCP(65001)
        kernel32.SetConsoleOutputCP(65001)
    except:
        pass

class ProcessManager:
    """生产级进程管理器"""
    
    def __init__(self):
        self.processes = {}
        self.running = True
        self.restart_counts = {}
        self.max_restarts = 3
        
    def start_service(self, name, command, cwd=None, env_vars=None):
        """启动服务"""
        print(f"🚀 启动 {name}...")
        
        # 准备环境变量
        env = os.environ.copy()
        env.update({
            'PYTHONIOENCODING': 'utf-8',
            'PYTHONUNBUFFERED': '1',
            'PYTHONLEGACYWINDOWSSTDIO': '1',
        })
        if env_vars:
            env.update(env_vars)
            
        try:
            # 使用最稳定的启动方式
            process = subprocess.Popen(
                command,
                cwd=cwd,
                env=env,
                # 关键：不重定向输出，让服务直接在控制台显示
                # 这避免了所有编码和缓冲问题
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            )
            
            self.processes[name] = process
            self.restart_counts[name] = 0
            print(f"✅ {name} 已启动，PID: {process.pid}")
            return process
            
        except Exception as e:
            print(f"❌ 启动 {name} 失败: {e}")
            return None
    
    def check_service_health(self, name, health_url, timeout=10):
        """检查服务健康状态"""
        for i in range(timeout):
            try:
                response = requests.get(health_url, timeout=2)
                if response.status_code == 200:
                    print(f"✅ {name} 健康检查通过")
                    return True
            except:
                pass
            time.sleep(1)
        
        print(f"⚠️ {name} 健康检查超时")
        return False
    
    def monitor_processes(self):
        """监控所有进程"""
        while self.running:
            for name, process in list(self.processes.items()):
                if process.poll() is not None:
                    exit_code = process.returncode
                    print(f"\n❌ {name} 意外停止，退出码: {exit_code}")
                    
                    # 自动重启逻辑
                    if self.restart_counts[name] < self.max_restarts:
                        self.restart_counts[name] += 1
                        print(f"🔄 重启 {name} ({self.restart_counts[name]}/{self.max_restarts})...")
                        self._restart_service(name)
                    else:
                        print(f"❌ {name} 重启次数达到上限，停止重启")
                        
            time.sleep(3)
    
    def _restart_service(self, name):
        """重启指定服务"""
        if name == "Backend":
            new_process = self.start_service(
                "Backend",
                [sys.executable, "main.py"],
                cwd=Path(__file__).parent / "backend"
            )
            if new_process:
                time.sleep(3)
                if self.check_service_health("Backend", "http://localhost:8002/health"):
                    print(f"✅ {name} 重启成功")
                    self.restart_counts[name] = 0
                    
        elif name == "Bot":
            new_process = self.start_service(
                "Bot",
                [sys.executable, "main.py"],
                env_vars={'DISABLE_PROCESS_CHECK': '1'}  # 禁用进程检查
            )
            if new_process:
                print(f"✅ {name} 重启成功")
                self.restart_counts[name] = 0
    
    def stop_all(self):
        """停止所有服务"""
        print("\n🛑 正在停止所有服务...")
        self.running = False
        
        for name, process in self.processes.items():
            try:
                print(f"⏹️ 停止 {name}...")
                if sys.platform == "win32":
                    # Windows: 发送 CTRL_BREAK_EVENT
                    os.kill(process.pid, signal.CTRL_BREAK_EVENT)
                else:
                    process.terminate()
                
                # 等待进程优雅退出
                try:
                    process.wait(timeout=5)
                    print(f"✅ {name} 已停止")
                except subprocess.TimeoutExpired:
                    # 强制杀死
                    process.kill()
                    print(f"💀 强制停止 {name}")
                    
            except Exception as e:
                print(f"⚠️ 停止 {name} 时出错: {e}")
        
        print("✅ 所有服务已停止")

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 TRON 能量助手 - 生产级启动器")
    print("=" * 60)
    print("✨ 特性: 自动重启、健康监控、编码兼容")
    print("-" * 60)
    
    manager = ProcessManager()
    
    # 注册信号处理器
    def signal_handler(signum, frame):
        manager.stop_all()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 启动后端服务
        backend = manager.start_service(
            "Backend",
            [sys.executable, "main.py"],
            cwd=Path(__file__).parent / "backend"
        )
        
        if not backend:
            print("❌ 后端服务启动失败，退出")
            return
        
        # 等待后端服务启动
        print("⏳ 等待后端服务启动...")
        time.sleep(5)
        
        # 检查后端健康状态
        if not manager.check_service_health("Backend", "http://localhost:8002/health", 15):
            print("❌ 后端服务健康检查失败")
            return
        
        # 启动 Bot 服务（禁用进程检查）
        bot = manager.start_service(
            "Bot",
            [sys.executable, "main.py"],
            env_vars={'DISABLE_PROCESS_CHECK': '1'}  # 禁用Bot的进程检查
        )
        
        if not bot:
            print("❌ Bot服务启动失败，退出")
            return
        
        # 显示状态信息
        print("\n" + "=" * 60)
        print("🎉 TRON 能量助手已成功启动！")
        print("\n📊 服务状态:")
        print(f"  🌐 后端API: http://localhost:8002 (PID: {backend.pid})")
        print(f"  🤖 Telegram Bot: 运行中 (PID: {bot.pid})")
        print("\n💡 功能特性:")
        print("  ✅ 自动故障检测和重启")
        print("  ✅ 服务健康监控")
        print("  ✅ 优雅关闭处理")
        print("  ✅ 编码问题完全解决")
        print("\n🎮 控制说明:")
        print("  📊 查看状态: 访问 http://localhost:8002/health")
        print("  🛑 停止服务: 按 Ctrl+C")
        print("=" * 60)
        
        # 启动监控线程
        monitor_thread = threading.Thread(target=manager.monitor_processes, daemon=True)
        monitor_thread.start()
        
        # 主循环 - 简单等待
        while manager.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)
    except Exception as e:
        print(f"\n💥 启动器异常: {e}")
        manager.stop_all()

if __name__ == "__main__":
    main()