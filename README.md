# PsyChat (原 0421PysChat)

PsyChat 是一个基于 RAG (Retrieval-Augmented Generation) 架构的心理健康聊天应用。它旨在利用大型语言模型和本地知识库，为用户提供情感支持和心理健康信息。

## 项目目标

*   提供一个安全、私密的环境，让用户可以与 AI 心理助手交流。
*   利用 RAG 技术，结合通用语言模型能力和专业的心理健康知识库，提供更准确、相关的回复。
*   探索 AI 在心理健康支持领域的应用。

## 技术栈

*   **前端**: Vue.js 3, Element Plus, Axios, Vite
*   **后端**: Python 3, FastAPI, Uvicorn, Pymysql, python-dotenv
*   **RAG 引擎**: AnythingLLM (管理知识库、嵌入、检索和 LLM 交互)
*   **数据库**: MySQL (存储原始资源文本)
*   **LLM**: DeepSeek API (或其他兼容 OpenAI 的 API)

## 架构

本项目采用前后端分离架构，并集成 AnythingLLM 作为 RAG 后端。详细架构请参考 [RAG_IMPLEMENTATION.md](./RAG_IMPLEMENTATION.md)。

## 快速开始

### 环境要求

*   Node.js (推荐 v16+)
*   Python (推荐 3.10+)
*   MySQL
*   AnythingLLM Desktop

### 后端设置

1.  进入 `backend` 目录: `cd backend`
2.  创建并激活虚拟环境 (例如: `python -m venv .venv` 和 `source .venv/bin/activate` 或 `.\.venv\Scripts\activate`)
3.  安装依赖: `pip install -r requirements.txt`
4.  创建 `.env` 文件: 复制 `backend/.env.example` 为 `backend/.env`，并根据你的环境配置填充实际值 (数据库凭据, AnythingLLM URL/Slug/Key 等)。 **不要将你的 `.env` 文件提交到版本控制。**
5.  运行 FastAPI 服务: `uvicorn main:app --reload --host 127.0.0.1 --port 8000` 或使用 VSCode 的 `Python: FastAPI` 启动配置。

### 前端设置

1.  进入 `frontend` 目录: `cd frontend`
2.  安装依赖: `npm install`
3.  启动开发服务器: `npm run dev`
4.  浏览器访问 Vite 提供的地址 (通常是 `http://localhost:5173`)。

### AnythingLLM 设置

1.  启动 AnythingLLM Desktop。
2.  按照 [RAG_IMPLEMENTATION.md](./RAG_IMPLEMENTATION.md) 中的指南配置 LLM Provider, Embedding Model, 创建 Workspace 并上传知识文档。
3.  确保 AnythingLLM 正在运行，并且后端 `.env` 文件中的配置正确指向它。

## 贡献

请参考 [CONTRIBUTING.md](./CONTRIBUTING.md)。

## 许可

本项目采用 [Apache License 2.0](./LICENSE)。
