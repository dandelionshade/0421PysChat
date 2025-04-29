# PsyChat RAG 实现指南

## 基于 AnythingLLM 的 RAG 架构

本文档详细描述了 PsyChat 项目中使用 AnythingLLM 实现检索增强生成(RAG)的架构设计和开发流程。

### RAG 架构概览

![RAG 架构](./docs/images/rag_architecture.png)

#### 核心组件

1. **前端 (Vue.js + Element Plus)**
   - 负责用户界面和与后端 API 的交互
   - 聊天界面和资源导航页面

2. **后端 (FastAPI + MySQL)**
   - 接收前端的聊天请求
   - 转发请求到 AnythingLLM API
   - 处理响应并返回给前端
   - 提供心理资源导航数据 API

3. **AnythingLLM (RAG 引擎)**
   - 作为独立应用运行
   - 处理文档上传、切块、嵌入和向量存储
   - 执行相似性搜索检索相关文档
   - 生成基于检索结果的 LLM 回复

4. **数据库 (MySQL)**
   - 存储原始心理资源文本
   - 存储用户信息和应用配置

## AnythingLLM 优势

AnythingLLM 作为预置的 RAG 后端具有以下优势:

1. **开箱即用**: 提供完整的 RAG 应用，包含图形界面管理文档、配置模型和测试聊天
2. **简化开发**: 封装了文档加载、切块、嵌入、向量存储、检索和 LLM 交互的复杂流程
3. **API 支持**: 提供 API 接口，允许后端与其交互
4. **模型兼容性**: 支持多种 LLM API，包括 DeepSeek API
5. **Windows 友好**: 提供桌面应用程序，可在 Windows 11 上运行和管理

## 详细实现步骤

### 阶段一: 配置和准备 AnythingLLM

1. **运行 AnythingLLM**
   - 启动 Windows 桌面应用程序

2. **配置 LLM Provider**
   - 进入设置 (Settings)
   - 选择 "兼容 OpenAI 的 URL"
   - 填入 DeepSeek API URL: `https://api.deepseek.com/v1`
   - 填入 DeepSeek API Key
   - 选择合适的模型 (如 `deepseek-chat`)
   - 保存并测试连接

3. **配置 Embedding Model**
   - 进入设置 (Settings)
   - 选择 Embedding Engine
   - 推荐使用中文模型如 `bge-base-zh-v1.5`

4. **创建 Workspace**
   - 创建名为 "MentalHealthBot" 的新 Workspace

5. **上传知识文档**
   - 从 MySQL 导出心理资源为 txt 或 pdf 文件
   - 在 Workspace 界面上传文档
   - AnythingLLM 自动进行文档处理

6. **配置 Workspace Prompt**
   - 设置 System Prompt，定义聊天机器人角色:

   你是一位专业、善解人意的心理健康顾问，名为"心理助手"。你的职责是提供情感支持和基于证据的心理健康信息。

   请遵循以下原则：
   1. 提供准确、基于科学的心理健康信息，优先引用知识库中的内容
   2. 保持温暖、同理但专业的语气
   3. 不提供具体药物、诊断或治疗建议，而是鼓励用户寻求专业帮助
   4. 识别潜在危机情况，并建议用户联系紧急服务或心理健康热线
   5. 保持文化敏感性和包容性
   6. 不讨论政治、宗教或其他争议话题
   7. 确保回复符合道德标准和专业伦理

   当用户表现出以下迹象时，提供危机资源信息：
   - 自伤或自杀想法
   - 伤害他人的想法
   - 极度情绪困扰
   - 精神病性症状

   危机资源信息：
   - 全国心理援助热线: 400-161-9995
   - 自杀干预热线: 010-82951332
   - 危机情况请拨打: 110 或 120

   始终记住，你不是替代专业心理健康服务，而是提供支持和信息的辅助工具。

7. **测试聊天**
   - 在 AnythingLLM 界面进行对话测试
   - 确认 RAG 流程工作正常

8. **获取 API 信息**
   - 记录 AnythingLLM 的本地运行地址 (如 `http://localhost:3001`)
   - 获取 API Key (如果已设置)
   - 确认聊天 API 路径 (如 `/api/v1/workspace/{workspace_slug}/chat`)

### 阶段二: 后端 API 调整 (FastAPI)

1. **更新依赖**
   - 移除 `sentence-transformers` 和 `chromadb`
   - 添加 `requests` 或 `httpx`

2. **修改聊天端点**
   - 调整 `/api/chat` 端点，使其转发请求到 AnythingLLM API

   ```python
   @app.post("/api/chat", response_model=ChatResponse)
   async def chat_endpoint(request: ChatRequest):
       user_query = request.message
       logger.info(f"Received query: {user_query}")

       # 调用 AnythingLLM API
       anythingllm_chat_url = f"{ANYTHINGLLM_API_BASE_URL}/api/v1/workspace/{ANYTHINGLLM_WORKSPACE_SLUG}/chat"
       headers = {
           "Content-Type": "application/json",
       }
       if ANYTHINGLLM_API_KEY:
           headers["Authorization"] = f"Bearer {ANYTHINGLLM_API_KEY}"

       payload = {
           "message": user_query,
           "mode": "chat"
       }

       try:
           # 使用 httpx 实现异步请求
           async with httpx.AsyncClient(timeout=60) as client:
               response = await client.post(anythingllm_chat_url, headers=headers, json=payload)
               
           response.raise_for_status()
           result = response.json()
           
           # 解析 AnythingLLM 响应
           reply_content = result.get("textResponse") or result.get("response", {}).get("text")
           if not reply_content:
                reply_content = "抱歉，无法获取有效回复。"
                
           return ChatResponse(reply=reply_content.strip())
           
       except Exception as e:
           logger.error(f"Error in chat endpoint: {e}")
           raise HTTPException(status_code=500, detail="内部服务器错误")
   ```

3. **更新环境配置**
   - 在 `.env` 文件中添加:

   ANYTHINGLLM_API_BASE_URL=<http://localhost:3001>
   ANYTHINGLLM_WORKSPACE_SLUG=mentalhealthbot
   ANYTHINGLLM_API_KEY=your_api_key_if_needed

### 阶段三: 前端开发

前端保持不变，继续通过 `/api/chat` 和 `/api/resources` 与后端通信。

### 阶段四: 数据库设计

保持原有 MySQL 数据库设计，主要用于:

1. 存储心理健康资源原始文本
2. 提供资源导航数据
3. (可选) 存储用户信息和应用配置

## 数据流程

1. **文档处理流程**:
   - 从 MySQL 导出心理资源
   - 上传到 AnythingLLM
   - AnythingLLM 处理并存储为向量

2. **聊天流程**:
   - 用户在前端发送消息
   - 前端将消息发送到后端 `/api/chat`
   - 后端转发到 AnythingLLM API
   - AnythingLLM 执行:
     - 将用户问题转为向量
     - 在向量数据库中搜索相似内容
     - 结合检索内容和 System Prompt 生成回复
   - 回复返回给后端，再转发到前端

## 部署考量

1. **AnythingLLM 部署**
   - 开发阶段可作为桌面应用运行
   - 生产环境可通过 Docker 部署

2. **性能优化**
   - 调整 AnythingLLM 中的切块大小和重叠参数
   - 优化 embedding 模型选择
   - 调整检索参数 (k值、相似度阈值)

3. **系统资源需求**
   - AnythingLLM 需要足够的内存和处理能力
   - 建议至少 8GB RAM 和 4 核 CPU

## 优势和注意事项

### 优势

1. **开发效率**: 无需实现复杂的 RAG 管道
2. **易于管理**: 通过图形界面管理知识库
3. **降低门槛**: 减少对 RAG 底层技术的要求
4. **功能完善**: 利用成熟 RAG 应用的特性和优化

### 注意事项

1. **依赖外部应用**: 需确保 AnythingLLM 稳定运行
2. **资源消耗**: AnythingLLM 会占用系统资源
3. **API 兼容性**: 需遵循 AnythingLLM API 的格式和限制
4. **系统提示关键**: 精心设计 System Prompt 直接影响最终效果
5. **更新维护**: 随 AnythingLLM 版本更新而调整集成方式

## 后续优化方向

1. **多语言支持**: 选择更适合中文的 embedding 模型
2. **自定义插件**: 开发 AnythingLLM 插件扩展功能
3. **反馈机制**: 实现用户反馈收集和模型响应调整
4. **会话管理**: 利用 AnythingLLM 的会话持久化功能
5. **高级检索**: 探索 HyDE (Hypothetical Document Embeddings) 等技术

## 参考资源

1. [AnythingLLM 官方文档](https://github.com/Mintplex-Labs/anything-llm)
2. [AnythingLLM API 文档](https://docs.anythingllm.com/api-reference/introduction)
3. [DeepSeek API 文档](https://platform.deepseek.com/docs)
4. [RAG 实现最佳实践](https://www.pinecone.io/learn/retrieval-augmented-generation/)
