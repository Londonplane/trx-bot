# -*- coding: utf-8 -*-
"""
Windows 编码修复工具
解决 Windows 下 Python 程序的编码问题
"""

import os
import sys
import codecs

def fix_windows_encoding():
    """修复 Windows 编码问题"""
    if sys.platform != "win32":
        return
    
    # 设置环境变量
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONLEGACYWINDOWSSTDIO'] = '1'
    
    # 设置控制台编码
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleCP(65001)
        kernel32.SetConsoleOutputCP(65001)
    except:
        pass
    
    # 重新包装 stdout/stderr
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')

# 在模块导入时自动修复
fix_windows_encoding()