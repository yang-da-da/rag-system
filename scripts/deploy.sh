#!/bin/bash

# 金融RAG系统部署脚本
set -e

echo "🚀 开始部署金融RAG系统..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p data
mkdir -p logs
mkdir -p ssl

# 检查环境变量文件
if [ ! -f .env ]; then
    echo "📝 创建环境变量文件..."
    cat > .env << EOF
# 应用配置
APP_NAME=金融领域专有名词标准化系统
APP_VERSION=1.0.0
DEBUG=false

# 数据库配置
MILVUS_HOST=milvus
MILVUS_PORT=19530
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# 日志配置
LOG_LEVEL=INFO
EOF
fi

# 停止现有服务
echo "🛑 停止现有服务..."
docker-compose down --remove-orphans

# 清理旧镜像（可选）
if [ "$1" = "--clean" ]; then
    echo "🧹 清理旧镜像..."
    docker system prune -f
fi

# 构建和启动服务
echo "🔨 构建和启动服务..."
docker-compose up --build -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 健康检查
echo "🏥 执行健康检查..."
if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "✅ 后端服务健康检查通过"
else
    echo "❌ 后端服务健康检查失败"
fi

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ 前端服务健康检查通过"
else
    echo "❌ 前端服务健康检查失败"
fi

echo "🎉 部署完成！"
echo "📱 前端地址: http://localhost:3000"
echo "🔧 后端地址: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
echo "🗄️  Milvus控制台: http://localhost:9001"
echo "📊 MinIO控制台: http://localhost:9000"

# 显示日志
echo "📋 显示服务日志..."
docker-compose logs --tail=20
