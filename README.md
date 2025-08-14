# 📊 金融领域专有名词标准化系统

基于RAG（检索增强生成）技术的金融术语标准化和智能处理系统，致力于提升金融文本处理的自动化与精准度。


## ✨ 系统功能

| 功能 | 描述 |
|------|------|
| **金融术语标准化** | 将非标准金融术语精准映射到标准术语库 |
| **金融实体识别** | 智能识别文本中的金融实体（公司、产品、指标等） |
| **金融缩写扩展** | 自动将金融领域缩写转换为完整术语表达 |
| **金融文本生成** | 基于专业金融知识生成符合规范的专业文本 |
| **金融拼写纠正** | 精准识别并纠正金融术语中的拼写错误 |


## 🛠️ 技术架构

| 模块 | 技术栈 |
|------|--------|
| **后端** | FastAPI + Python 3.13 |
| **前端** | React + Tailwind CSS |
| **向量数据库** | Milvus |
| **嵌入模型** | BGE-M3 |
| **大语言模型** | Ollama (Qwen2.5:7B) |


## 🚀 快速开始

### 环境要求

- **Docker方式（推荐）**: Docker 20.10+ 和 Docker Compose 2.0+
- **本地开发**: Python 3.11+ 和 Node.js 18+
- **内存要求**: 8GB+ RAM（生产环境建议16GB+）


#### 方式一：Docker部署（推荐）

1. **克隆项目**
```bash
git clone <repository-url>
cd financial-rag-system
```

2. **一键部署**
```bash
# 给脚本执行权限
chmod +x scripts/deploy.sh

# 执行部署
./scripts/deploy.sh

# 清理部署（如需）
./scripts/deploy.sh --clean
```

3. **服务访问地址**
| 服务 | 地址 |
|------|------|
| 前端应用 | http://localhost:3000 |
| 后端API | http://localhost:8000 |
| API文档 | http://localhost:8000/docs |
| Milvus控制台 | http://localhost:9001 |
| MinIO控制台 | http://localhost:9000 |


#### 方式二：本地开发

1. **后端设置**
```bash
cd backend
python -m venv venv

# Windows激活环境
venv\Scripts\activate
# Linux/Mac激活环境
source venv/bin/activate

pip install -r requirements.txt
```

2. **前端设置**
```bash
cd frontend
npm install
```

3. **启动服务**
```bash
# 启动后端
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 启动前端
cd frontend
npm start
```


## 📊 数据说明

系统内置专业金融术语数据库，包含**15,886条**标准术语，全面覆盖：

- 🏦 银行术语  
- 📈 证券术语  
- 💹 投资术语  
- 🛡️ 保险术语  
- 🔄 衍生品术语  
- 📉 风险管理术语  


## 📁 项目结构

```
financial-rag-system/
├── backend/                 # 后端服务
│   ├── main.py             # 主应用入口
│   ├── config.py           # 配置管理
│   ├── middleware.py       # 中间件
│   ├── services/           # 业务服务
│   └── utils/              # 工具函数
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── components/     # 组件
│   │   ├── services/       # API服务
│   │   └── pages/          # 页面
│   └── package.json
├── scripts/                # 部署脚本
├── docker-compose.yml      # 容器编排
├── Dockerfile              # 后端容器
└── README.md
```


## 💻 开发指南

### 代码规范
- 后端：使用 `black` 格式化Python代码，遵循PEP 8规范
- 前端：使用 `prettier` 格式化代码，遵循ESLint规则

### 测试命令
```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm test
```

### 代码质量检查
```bash
# 后端检查
cd backend
flake8 .
black --check .
isort --check-only .

# 前端检查
cd frontend
npm run lint
npm run type-check
```


## ⚡ 性能优化

- 采用异步处理提升系统并发能力
- 实现请求限流与智能缓存机制
- 优化向量搜索算法，提升检索速度
- 前端实现代码分割与组件懒加载


## 📋 监控和日志

- 集成Prometheus指标收集系统
- 实现结构化日志记录与分析
- 实时监控API调用性能
- 完善的健康检查与告警机制


## 📜 许可证

本项目采用 [MIT License](LICENSE) 开源协议。