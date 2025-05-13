# PsyChat (原 0421PysChat)

PsyChat 是一个基于 RAG (Retrieval-Augmented Generation) 架构的心理健康聊天应用。它旨在利用大型语言模型和本地知识库，为用户提供情感支持和心理健康信息。

## 项目目标

* 提供一个安全、私密的环境，让用户可以与 AI 心理助手交流。
* 利用 RAG 技术，结合通用语言模型能力和专业的心理健康知识库，提供更准确、相关的回复。
* 探索 AI 在心理健康支持领域的应用。

## 技术栈

* **前端**: Vue.js 3, Element Plus, Axios, Vite
* **后端**: Python 3, FastAPI, Uvicorn, Pymysql, python-dotenv
* **RAG 引擎**: AnythingLLM (管理知识库、嵌入、检索和 LLM 交互)
* **数据库**: MySQL (存储原始资源文本)
* **LLM**: DeepSeek API (或其他兼容 OpenAI 的 API)

## 架构

本项目采用前后端分离架构，并集成 AnythingLLM 作为 RAG 后端。详细架构请参考 [docs/RAG_IMPLEMENTATION.md](./docs/RAG_IMPLEMENTATION.md)。

## 快速开始

### 环境要求

* Node.js (推荐 v16+)
* Python (推荐 3.10+)
* MySQL
* AnythingLLM Desktop

### 使用脚本快速设置

1. 克隆仓库并进入项目目录
2. 运行设置脚本: `./scripts/setup.sh`
3. 按照提示配置环境变量
4. 启动开发环境: `npm start`

### 手动设置

#### 后端设置

1. 进入 `backend` 目录: `cd backend`
2. 创建并激活虚拟环境 (例如: `python -m venv .venv` 和 `source .venv/bin/activate` 或 `.\.venv\Scripts\activate`)
3. 安装依赖: `pip install -r requirements.txt`
4. 创建 `.env` 文件: 复制 `backend/.env.example` 为 `backend/.env`，并根据你的环境配置填充实际值 (数据库凭据, AnythingLLM URL/Slug/Key 等)。 **不要将你的 `.env` 文件提交到版本控制。**
5. 运行 FastAPI 服务: `uvicorn main:app --reload --host 127.0.0.1 --port 8000` 或使用 VSCode 的 `Python: FastAPI` 启动配置。

#### 前端设置

1. 进入 `frontend` 目录: `cd frontend`
2. 安装依赖: `npm install`
3. 启动开发服务器: `npm run dev`
4. 浏览器访问 Vite 提供的地址 (通常是 `http://localhost:5173`)。

### AnythingLLM 设置

1. 启动 AnythingLLM Desktop。
2. 按照 [docs/RAG_IMPLEMENTATION.md](./docs/RAG_IMPLEMENTATION.md) 中的指南配置 LLM Provider, Embedding Model, 创建 Workspace 并上传知识文档。
3. 确保 AnythingLLM 正在运行，并且后端 `.env` 文件中的配置正确指向它。

## 部署

使用 Docker Compose 进行部署:

```bash
# 复制并编辑环境变量
cp .env.example .env
# 编辑 .env 文件...

# 运行部署脚本
./scripts/deploy.sh
```

## 项目结构

```
└── PsyChat/
    ├── backend/          # FastAPI 后端
    ├── database/         # 数据库初始化脚本
    ├── docs/             # 项目文档
    ├── frontend/         # Vue 3 前端
    ├── scripts/          # 部署和设置脚本
    └── docker-compose.yml # Docker 配置
```

## 贡献指南

### 行为准则

* 尊重所有参与者
* 接受建设性批评
* 专注于项目最佳利益
* 保持专业沟通态度

### 如何贡献

#### 报告Bug

1. 使用GitHub Issues创建新的问题
2. 使用清晰的标题描述问题
3. 详细说明重现步骤
4. 描述预期与实际行为
5. 如可能，添加截图

#### 提交功能请求

1. 创建新的Issue并标记为"enhancement"
2. 清晰描述需求和用例
3. 如可能，提出实现方案

#### 开发流程

1. Fork项目仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交Pull Request

### 代码风格

* 遵循项目现有的代码风格
* 使用有意义的变量和函数名
* 编写清晰的注释
* 适当添加文档

### 提交信息规范

采用[Conventional Commits](https://www.conventionalcommits.org/)规范:

<类型>[可选作用域]: <描述>

[可选正文]

[可选页脚]

类型包括:

* `feat`: 新功能
* `fix`: 错误修复
* `docs`: 文档更新
* `style`: 代码样式调整
* `refactor`: 代码重构
* `perf`: 性能优化
* `test`: 测试相关
* `chore`: 构建过程或辅助工具变动

## 许可

本项目采用 [Apache License 2.0](./LICENSE)。

## 感谢

感谢所有对本项目做出贡献的人！项目的进步离不开社区每一位成员的参与。
