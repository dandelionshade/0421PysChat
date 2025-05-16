#!/usr/bin/env python
"""
开发环境设置脚本
- 检查所需依赖
- 设置环境变量
- 初始化数据库
"""
import os
import sys
import subprocess
import shutil

def check_requirements():
    """检查是否安装了所需依赖"""
    print("检查依赖...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("错误: 需要Python 3.8+")
        return False
    
    # 检查所需命令
    required_commands = ["docker", "docker-compose", "npm", "pip"]
    for cmd in required_commands:
        if shutil.which(cmd) is None:
            print(f"错误: 未找到命令 '{cmd}'")
            return False
            
    return True

def setup_env():
    """设置环境变量文件"""
    if not os.path.exists(".env"):
        print("创建.env文件...")
        shutil.copy(".env.example", ".env")
        print("请编辑.env文件填入你的实际配置值")

def setup_database():
    """设置开发数据库"""
    print("初始化开发数据库...")
    # 这里可以添加数据库初始化逻辑，如运行Docker容器、执行SQL脚本等

def main():
    """主函数"""
    print("设置PsyChat开发环境...")
    
    if not check_requirements():
        return 1
        
    setup_env()
    setup_database()
    
    print("\n开发环境设置完成！")
    print("\n要启动开发服务器:")
    print("1. 启动后端: cd backend && uvicorn main:app --reload")
    print("2. 启动前端: cd frontend && npm run dev")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
