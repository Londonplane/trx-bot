#!/usr/bin/env python3
"""
关闭Bot脚本 - 快速停止所有运行中的Bot实例
"""

import os
import sys

try:
    import psutil
except ImportError:
    print("❌ psutil库未安装")
    print("请运行: pip install psutil")
    sys.exit(1)

def stop_all_bot_instances():
    """停止所有Bot实例"""
    print("🔍 查找运行中的Bot实例...")
    
    current_pid = os.getpid()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(script_dir, 'main.py')
    
    running_instances = []
    
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
                    
                    running_instances.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': ' '.join(cmdline)
                    })
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
                
    except Exception as e:
        print(f"❌ 检查进程时出错: {e}")
        return False
    
    if not running_instances:
        print("✅ 没有发现运行中的Bot实例")
        return True
    
    print(f"🔴 发现 {len(running_instances)} 个运行中的Bot实例:")
    for instance in running_instances:
        print(f"   - PID: {instance['pid']}, 命令: {instance['cmdline'][:80]}...")
    
    print("🛑 正在停止所有Bot实例...")
    
    success_count = 0
    for instance in running_instances:
        pid = instance['pid']
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            
            # 等待进程结束
            try:
                proc.wait(timeout=5)
                success_count += 1
                print(f"   ✅ 进程 {pid} 已停止")
            except psutil.TimeoutExpired:
                # 强制杀死
                proc.kill()
                success_count += 1
                print(f"   ✅ 进程 {pid} 已强制停止")
                
        except psutil.NoSuchProcess:
            success_count += 1
            print(f"   ✅ 进程 {pid} 已不存在")
        except Exception as e:
            print(f"   ❌ 停止进程 {pid} 失败: {e}")
    
    if success_count == len(running_instances):
        print("=" * 50)
        print("✅ 所有Bot实例已成功停止")
        print("=" * 50)
        return True
    else:
        print("=" * 50)
        print(f"⚠️  停止了 {success_count}/{len(running_instances)} 个实例")
        print("建议使用任务管理器手动停止剩余进程")
        print("=" * 50)
        return False

def main():
    print("=" * 50)
    print("🛑 TRON Bot 关闭器")
    print("=" * 50)
    
    success = stop_all_bot_instances()
    
    if success:
        print("Bot已完全停止，可以安全重启")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()