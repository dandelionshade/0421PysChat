#!/bin/bash

# PsyChat项目设置脚本

set -e # 当脚本出错时退出

echo "=== PsyChat项目设置开始 ==="

# 检查必要的工具
echo "检查必要工具..."
command -v docker >/dev/null 2>&1 || { echo "需要安装Docker"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "需要安装Docker Compose"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "需要安装Node.js"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "需要安装Python 3"; exit 1; }

# 创建环境文件
echo "创建环境文件..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "已创建根目录 .env 文件，请根据需要编辑配置"
fi

if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "已创建后端 .env 文件，请根据需要编辑配置"
fi

# 初始化数据库
echo "正在初始化数据库..."
docker-compose up -d db
echo "等待数据库启动..."
sleep 10  # 等待数据库完全启动

# 安装依赖
echo "安装前端依赖..."
npm run install:all

echo "安装后端依赖..."
cd backend
python3 -m venv .venv
source .venv/bin/activate || . .venv/bin/activate
pip install -r requirements.txt
cd ..

echo "=== PsyChat项目设置完成 ==="
echo "请编辑 .env 和 backend/.env 文件，设置必要的配置"
echo "然后运行 'npm start' 启动开发环境"
echo "或运行 './scripts/deploy.sh' 部署生产环境"
