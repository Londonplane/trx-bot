import os
import subprocess

def find_bot_processes():
    """查找运行中的Bot进程"""
    print("查找运行中的Bot进程...")
    
    try:
        # Windows版本 - 使用tasklist
        result = subprocess.run(['tasklist', '/FO', 'CSV'], 
                              capture_output=True, text=True, encoding='gbk')
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            python_processes = []
            
            for line in lines:
                if 'python.exe' in line.lower():
                    # 解析CSV格式的输出
                    parts = line.strip().split(',')
                    if len(parts) >= 2:
                        name = parts[0].strip('"')
                        pid = parts[1].strip('"')
                        python_processes.append((name, pid))
            
            if python_processes:
                print(f"发现 {len(python_processes)} 个Python进程:")
                for name, pid in python_processes:
                    print(f"  - {name} (PID: {pid})")
                    
                print(f"\n建议操作:")
                print(f"1. 按 Ctrl+C 如果Bot在当前终端运行")
                print(f"2. 或者使用任务管理器关闭python.exe进程")
                print(f"3. 或者执行: taskkill /PID <进程ID> /F")
                
                # 提供具体的kill命令
                for name, pid in python_processes:
                    print(f"   taskkill /PID {pid} /F")
            else:
                print("没有发现运行中的Python进程")
        else:
            print("无法查询进程列表")
            
    except Exception as e:
        print(f"查询进程时出错: {e}")

if __name__ == "__main__":
    find_bot_processes()