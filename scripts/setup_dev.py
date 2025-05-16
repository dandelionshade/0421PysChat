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
    
    # 检查所需Python包
    required_packages = ["pytest", "playwright", "fastapi", "httpx", "pymysql"]
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"缺少所需Python包: {', '.join(missing_packages)}")
        install = input("是否自动安装缺少的包? (y/n): ")
        if install.lower() == 'y':
            subprocess.run([sys.executable, "-m", "pip", "install", *missing_packages])
            
            # 特殊处理: playwright需要安装浏览器
            if "playwright" in missing_packages:
                print("安装Playwright浏览器...")
                subprocess.run([sys.executable, "-m", "playwright", "install"])
        else:
            print(f"请手动安装缺少的包: pip install {' '.join(missing_packages)}")
            if "playwright" in missing_packages:
                print("安装完Playwright后，还需要安装浏览器: python -m playwright install")
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
