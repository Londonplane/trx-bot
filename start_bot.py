#!/usr/bin/env python3
"""
智能Bot启动脚本 - 自动检查并关闭已运行的实例
"""

import os
import sys
import time
import subprocess
import signal
import psutil
from pathlib import Path

def find_running_bot_processes():
    """查找运行中的Bot进程"""
    current_pid = os.getpid()
    current_script = os.path.abspath(__file__)
    main_script = os.path.join(os.path.dirname(current_script), 'main.py')
    
    running_processes = []
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # 跳过当前进程
                if proc.info['pid'] == current_pid:
                    continue
                
                cmdline = proc.info['cmdline']
                if not cmdline:
                    continue
                
                # 检查是否是Python进程运行main.py
                if (len(cmdline) >= 2 and 
                    ('python' in cmdline[0].lower() or cmdline[0].endswith('python.exe')) and
                    ('main.py' in ' '.join(cmdline) or main_script in ' '.join(cmdline))):
                    
                    running_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': ' '.join(cmdline)
                    })
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
                
    except Exception as e:
        print(f"查找进程时出错: {e}")
    
    return running_processes

def kill_process_tree(pid):
    """杀死进程及其子进程"""
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        
        # 先杀死子进程
        for child in children:
            try:
                child.terminate()
            except psutil.NoSuchProcess:
                pass
        
        # 等待子进程结束
        gone, alive = psutil.wait_procs(children, timeout=3)
        
        # 强制杀死仍存活的子进程
        for proc in alive:
            try:
                proc.kill()
            except psutil.NoSuchProcess:
                pass
        
        # 杀死父进程
        try:
            parent.terminate()
            parent.wait(timeout=3)
        except psutil.TimeoutExpired:
            parent.kill()
        except psutil.NoSuchProcess:
            pass
            
        return True
        
    except psutil.NoSuchProcess:
        return True  # 进程已经不存在
    except Exception as e:
        print(f"终止进程 {pid} 时出错: {e}")
        return False

def check_ports():
    """检查关键端口是否被占用"""
    ports_to_check = [8002]  # backend服务使用的端口
    occupied_ports = []
    
    for port in ports_to_check:
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == 'LISTEN':
                occupied_ports.append({
                    'port': port,
                    'pid': conn.pid
                })
                break
    
    return occupied_ports

def stop_existing_instances():
    """停止现有的Bot实例"""
    print("🔍 检查运行中的Bot实例...")
    
    # 查找Bot进程
    running_processes = find_running_bot_processes()
    
    if not running_processes:
        print("✅ 没有发现运行中的Bot实例")
        return True
    
    print(f"🔴 发现 {len(running_processes)} 个运行中的Bot实例:")
    for proc in running_processes:
        print(f"   - PID: {proc['pid']}, 命令: {proc['cmdline'][:100]}...")
    
    print("🛑 正在停止现有实例...")
    
    success_count = 0
    for proc in running_processes:
        pid = proc['pid']
        print(f"   停止进程 {pid}...")
        
        if kill_process_tree(pid):
            success_count += 1
            print(f"   ✅ 进程 {pid} 已停止")
        else:
            print(f"   ❌ 停止进程 {pid} 失败")
    
    if success_count == len(running_processes):
        print("✅ 所有Bot实例已停止")
        time.sleep(2)  # 等待进程完全清理
        return True
    else:
        print(f"⚠️  停止了 {success_count}/{len(running_processes)} 个实例")
        return False

def check_and_kill_port_processes():
    """检查并杀死占用关键端口的进程"""
    print("🔍 检查端口占用...")
    
    occupied_ports = check_ports()
    
    if not occupied_ports:
        print("✅ 关键端口未被占用")
        return True
    
    print(f"🔴 发现端口占用:")
    for port_info in occupied_ports:
        port = port_info['port']
        pid = port_info['pid']
        
        if pid:
            try:
                proc = psutil.Process(pid)
                print(f"   端口 {port} 被进程占用: PID {pid} ({proc.name()})")
                
                print(f"   停止占用端口 {port} 的进程 {pid}...")
                if kill_process_tree(pid):
                    print(f"   ✅ 进程 {pid} 已停止，端口 {port} 已释放")
                else:
                    print(f"   ❌ 停止进程 {pid} 失败")
                    
            except psutil.NoSuchProcess:
                print(f"   端口 {port} 占用进程已不存在")
        else:
            print(f"   端口 {port} 被占用，但无法获取进程信息")
    
    time.sleep(1)
    return True

def start_bot():
    """启动Bot"""
    main_script = os.path.join(os.path.dirname(__file__), 'main.py')
    
    if not os.path.exists(main_script):
        print(f"❌ 找不到 main.py 文件: {main_script}")
        return False
    
    print("🚀 启动Bot...")
    print(f"📁 工作目录: {os.getcwd()}")
    print(f"📄 启动脚本: {main_script}")
    print("-" * 60)
    
    try:
        # 使用当前Python解释器启动main.py
        os.execv(sys.executable, [sys.executable, main_script])
    except Exception as e:
        print(f"❌ 启动Bot失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🤖 TRON Bot 智能启动器")
    print("=" * 60)
    
    try:
        # 检查psutil是否可用
        import psutil
    except ImportError:
        print("❌ psutil库未安装，使用基础功能")
        print("   可以运行: pip install psutil 来获得完整功能")
        print("\n🚀 直接启动Bot...")
        start_bot()
        return
    
    # 停止现有实例
    if not stop_existing_instances():
        print("⚠️  部分实例停止失败，但仍将继续启动")
    
    # 检查端口占用
    check_and_kill_port_processes()
    
    print("\n" + "=" * 60)
    print("🎯 准备启动新的Bot实例...")
    print("=" * 60)
    
    # 启动Bot
    start_bot()

if __name__ == "__main__":
    main()