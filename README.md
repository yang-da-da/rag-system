# 金融领域专有名词标准化系统

基于RAG（检索增强生成）技术的金融术语标准化和智能处理系统。

## 系统功能

- **金融术语标准化**: 将非标准金融术语映射到标准金融术语库
- **金融实体识别**: 识别文本中的金融实体（公司、产品、指标等）
- **金融缩写扩展**: 将金融缩写扩展为完整术语
- **金融文本生成**: 基于金融知识生成专业文本
- **金融拼写纠正**: 纠正金融术语的拼写错误

## 技术架构

- **后端**: FastAPI + Python 3.13
- **前端**: React + Tailwind CSS
- **向量数据库**: Milvus
- **嵌入模型**: BGE-M3
- **大语言模型**: Ollama (Qwen2.5:7B)

## 快速开始

### 环境要求

- **Docker方式（推荐）**: Docker 20.10+ 和 Docker Compose 2.0+
- **本地开发**: Python 3.11+ 和 Node.js 18+
- **内存要求**: 8GB+ RAM

### 方式一：Docker部署（推荐）

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

# 或者清理部署
./scripts/deploy.sh --clean
```

3. **访问服务**
- 前端: http://localhost:3000
- 后端: http://localhost:8000
- API文档: http://localhost:8000/docs
- Milvus控制台: http://localhost:9001
- MinIO控制台: http://localhost:9000

### 方式二：本地开发

1. **后端设置**
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
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
# 后端
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 前端
cd frontend
npm start
```

## 数据说明

系统使用包含15,886条金融标准术语的数据库，涵盖：
- 投资术语
- 银行术语
- 保险术语
- 证券术语
- 衍生品术语
- 风险管理术语

## API文档

启动后端服务后，访问 `http://localhost:8000/docs` 查看完整的API文档。

## 项目结构

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

## 开发指南

### 代码规范
- 使用 `black` 格式化Python代码
- 使用 `prettier` 格式化前端代码
- 遵循PEP 8和ESLint规则

### 测试
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
# 后端
cd backend
flake8 .
black --check .
isort --check-only .

# 前端
cd frontend
npm run lint
npm run type-check
```

## 性能优化

- 使用异步处理提高并发性能
- 实现请求限流和缓存机制
- 优化向量搜索性能
- 前端代码分割和懒加载

## 监控和日志

- 集成Prometheus指标收集
- 结构化日志记录
- API调用性能监控
- 健康检查和告警

## 许可证

MIT License
