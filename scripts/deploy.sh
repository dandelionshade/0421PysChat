#!/bin/bash

# PsyChat项目部署脚本

set -e # 当脚本出错时退出

echo "=== PsyChat项目部署开始 ==="

# 检查必要的工具
echo "检查必要工具..."
command -v docker >/dev/null 2>&1 || { echo "需要安装Docker"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "需要安装Docker Compose"; exit 1; }

# 检查环境文件
if [ ! -f .env ]; then
    echo "未找到 .env 文件，正在创建模板..."
    cp .env.example .env
    echo "请编辑 .env 文件，设置必要的配置后重新运行此脚本"
    exit 1
fi

# 构建Docker镜像
echo "构建Docker镜像..."
docker-compose build

# 启动服务
echo "启动服务..."
docker-compose up -d

echo "=== PsyChat项目部署完成 ==="
echo "服务已启动："
echo "- 前端: http://localhost:$(grep FRONTEND_PORT .env | cut -d= -f2 || echo 80)"
echo "- 后端API: http://localhost:$(grep BACKEND_PORT .env | cut -d= -f2 || echo 8000)"
echo "- AnythingLLM API: $(grep ANYTHINGLLM_API_BASE_URL .env | cut -d= -f2 || echo http://localhost:3001)/v1"
echo ""
echo "可通过 'docker-compose logs -f' 查看服务日志"
echo "可通过 'docker-compose down' 停止服务"
