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

   ```
   # 主要角色：心理健康顾问

   ## 基本设定
   你是一位专业、善解人意的心理健康顾问，名为"心理助手"。你的职责是提供情感支持和基于证据的心理健康信息。

   ## 行为准则
   请遵循以下原则：
   1. 提供准确、基于科学的心理健康信息，优先引用知识库中的内容
   2. 保持温暖、同理但专业的语气
   3. 不提供具体药物、诊断或治疗建议，而是鼓励用户寻求专业帮助
   4. 识别潜在危机情况，并建议用户联系紧急服务或心理健康热线
   5. 保持文化敏感性和包容性
   6. 不讨论政治、宗教或其他争议话题
   7. 确保回复符合道德标准和专业伦理

   ## 危机干预
   当用户表现出以下迹象时，提供危机资源信息：
   - 自伤或自杀想法
   - 伤害他人的想法
   - 极度情绪困扰
   - 精神病性症状

   ## 资源信息
   危机资源信息：
   - 全国心理援助热线: 400-161-9995
   - 自杀干预热线: 010-82951332
   - 危机情况请拨打: 110 或 120

   ## 重要提示
   始终记住，你不是替代专业心理健康服务，而是提供支持和信息的辅助工具。
   ```

   - (可选) 高级角色配置，用于增强专业能力:
   
   ```
   # 扩展角色：心理模型专家

   ## 性格特征
   INTJ（内向直觉思维判断型）：专业、冷静、理性

   ## 专业背景
   心理模型专家致力于帮助用户深入理解人物的心理特点和行为模式，通过心理学原理分析人物的动机和行为。

   ## 核心能力
   1. 心理学知识储备
   2. 人物心理分析能力
   3. 角色构建和创意写作技巧

   ## 价值观
   1. 尊重个体差异，理解人物多样性
   2. 以科学的态度分析人物心理，避免偏见和刻板印象

   ## 工作方法
   1. 收集需求，明确角色定位
   2. 运用心理学原理分析心理特点
   3. 构建人物心理模型
   4. 提供角色构建建议
   5. 跟进反馈，调整优化
   6. 总结经验，提炼方法论
   ```

7. **测试聊天**
   - 在 AnythingLLM 界面进行对话测试
   - 确认 RAG 流程工作正常

8. **获取 API 信息**
   - 记录 AnythingLLM 的本地运行地址 (如 `http://localhost:3001`)
   - 获取 API Key (如果已设置)
   - 确认聊天 API 路径:
     - 一般工作空间聊天: `/api/v1/workspace/{workspace_slug}/chat`
     - 创建新聊天线程: `/api/v1/workspace/{workspace_slug}/thread/new`
     - 在现有线程中聊天: `/api/v1/workspace/{workspace_slug}/thread/{thread_slug}/chat`

### 阶段二: 后端 API 调整 (FastAPI)

1. **更新依赖**
   - 移除 `sentence-transformers` 和 `chromadb`
   - 添加 `requests` 或 `httpx`
   - (建议) 添加 `python-logging` (通常是标准库，但确保配置)

2. **修改聊天端点**
   - 调整 `/api/chat` 端点以支持线程化聊天，并使其转发请求到相应的 AnythingLLM API。
   - `ChatRequest` Pydantic 模型更新，增加可选的 `session_id: Optional[str]` 字段，用于客户端传递会话标识。

   ```python
   # main.py (FastAPI backend)
   # ... (确保导入必要的模块) ...

   # class ChatRequest(BaseModel):
   #     message: str
   #     session_id: Optional[str] = None # 新增字段，用于会话管理

   # class ChatResponse(BaseModel):
   #     reply: str

   # ... (app, logger, 配置变量定义) ...

   @app.post("/api/chat", response_model=ChatResponse)
   async def chat_endpoint(request: ChatRequest, client: httpx.AsyncClient = Depends(get_http_client)): # 示例依赖注入
       user_query = request.message
       session_id = request.session_id
       logger.info(f"Received query: {user_query}, session_id: {session_id}")

       if not ANYTHINGLLM_WORKSPACE_SLUG or not ANYTHINGLLM_API_BASE_URL:
           logger.error("AnythingLLM URL or workspace slug not configured.")
           raise HTTPException(status_code=500, detail="Server configuration error.")

       headers = {
           "Content-Type": "application/json",
       }
       if ANYTHINGLLM_API_KEY:
           headers["Authorization"] = f"Bearer {ANYTHINGLLM_API_KEY}"

       payload = {"message": user_query}
       anythingllm_chat_url = ""
       db_conn = None # 假设 get_db_connection() 用于获取数据库连接

       try:
           if session_id:
               db_conn = get_db_connection()
               with db_conn.cursor() as cursor:
                   cursor.execute("SELECT anythingllm_thread_id FROM chat_sessions WHERE id = %s", (session_id,))
                   session_row = cursor.fetchone()
                   
                   anythingllm_thread_id = None
                   if session_row and session_row.get("anythingllm_thread_id"):
                       anythingllm_thread_id = session_row["anythingllm_thread_id"]
                       logger.info(f"Using existing thread_id: {anythingllm_thread_id} for session: {session_id}")
                   else:
                       # 创建新的 AnythingLLM 线程
                       new_thread_url = f"{ANYTHINGLLM_API_BASE_URL}/api/v1/workspace/{ANYTHINGLLM_WORKSPACE_SLUG}/thread/new"
                       # New thread payload might be empty or require a name, e.g., json={} or json={"name": "New Chat"}
                       # Refer to AnythingLLM API docs for /thread/new payload
                       new_thread_response = await client.post(new_thread_url, headers=headers, json={}) 
                       new_thread_response.raise_for_status()
                       thread_data = new_thread_response.json()
                       anythingllm_thread_id = thread_data.get("slug") # Assuming 'slug' is the key for thread ID

                       if not anythingllm_thread_id:
                           raise HTTPException(status_code=500, detail="Failed to create or retrieve thread ID from LLM service.")
                       
                       # 将新的 anythingllm_thread_id 保存到 chat_sessions 表
                       if session_row: # 更新现有会话
                           cursor.execute("UPDATE chat_sessions SET anythingllm_thread_id = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                                          (anythingllm_thread_id, session_id))
                       else: # 创建新会话记录
                           cursor.execute("INSERT INTO chat_sessions (id, anythingllm_thread_id, name) VALUES (%s, %s, %s)",
                                          (session_id, anythingllm_thread_id, f"Session {session_id[:8]}"))
                       db_conn.commit()
                       logger.info(f"Saved new thread_id {anythingllm_thread_id} for session {session_id}")
               
               anythingllm_chat_url = f"{ANYTHINGLLM_API_BASE_URL}/api/v1/workspace/{ANYTHINGLLM_WORKSPACE_SLUG}/thread/{anythingllm_thread_id}/chat"
               # payload["mode"] = "chat" # 'mode' might not be needed or different for thread chat
           
           else # 无 session_id，使用通用工作空间聊天
               anythingllm_chat_url = f"{ANYTHINGLLM_API_BASE_URL}/api/v1/workspace/{ANYTHINGLLM_WORKSPACE_SLUG}/chat"
               payload["mode"] = "chat" # Ensure 'mode' is 'chat' for general workspace chat

           try:
               async with httpx.AsyncClient(timeout=60.0) as client: # Added timeout
                   response = await client.post(anythingllm_chat_url, headers=headers, json=payload)
                   response.raise_for_status()  # Raises an exception for 4XX/5XX responses
                   
               result = response.json()
               logger.info(f"AnythingLLM response: {result}")
               
               # Enhanced response parsing
               reply_content = result.get("textResponse") or result.get("response", {}).get("text")
               
               if not reply_content:
                    logger.warning("No valid reply content from AnythingLLM.")
                    reply_content = "抱歉，无法获取有效回复。"
                    
               return ChatResponse(reply=reply_content.strip())
               
           except httpx.HTTPStatusError as e:
               logger.error(f"HTTP error from AnythingLLM: {e.response.status_code} - {e.response.text}")
               raise HTTPException(status_code=e.response.status_code, detail=f"Error from LLM service: {e.response.text}")
           except httpx.RequestError as e:
               logger.error(f"Request error to AnythingLLM: {e}")
               raise HTTPException(status_code=503, detail=f"LLM service unavailable: {str(e)}")
           except Exception as e:
               logger.error(f"Error in chat endpoint: {e}", exc_info=True)
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

保持原有 MySQL 数据库设计，并对 `chat_sessions` 表进行扩展：

1. **`chat_sessions` 表**:
   - 新增 `anythingllm_thread_id VARCHAR(255) NULL` 列。
   - **用途**: 存储从 AnythingLLM 创建新线程时返回的 `threadSlug` (或类似标识符)。这允许 PsyChat 的会话与 AnythingLLM 中的特定聊天线程关联起来，实现持久化和上下文连贯的对话。
   - 添加索引 `idx_anythingllm_thread_id (anythingllm_thread_id)` 以优化查询。

2. 存储心理健康资源原始文本
3. 提供资源导航数据
4. (可选) 存储用户信息和应用配置

## 数据流程

1. **文档处理流程**:
   - 从 MySQL 导出心理资源
   - 上传到 AnythingLLM
   - AnythingLLM 处理并存储为向量

2. **聊天流程 (支持线程化会话)**:
   - 用户在前端发送消息，可选地附带一个 `session_id`。
   - 前端将消息和 `session_id` (如果存在) 发送到后端 `/api/chat`。
   - **后端逻辑**:
     - **如果提供了 `session_id`**:
       1. 后端查询 `chat_sessions` 表，查找与此 `session_id` 关联的 `anythingllm_thread_id`。
       2. **如果找到 `anythingllm_thread_id`**: 后端将用户消息发送到 AnythingLLM 的特定线程聊天API (`.../thread/{thread_id}/chat`)。
       3. **如果未找到 `anythingllm_thread_id` (或会话是新的)**:
          a. 后端首先调用 AnythingLLM 的创建新线程 API (`.../thread/new`)。
          b. 从响应中提取新的 `threadSlug` (即 `anythingllm_thread_id`)。
          c. 将此 `session_id` 和新的 `anythingllm_thread_id` 存储/更新到 `chat_sessions` 表中。
          d. 然后，将用户消息发送到新创建的线程的聊天 API (`.../thread/{new_thread_id}/chat`)。
     - **如果未提供 `session_id`**: 后端将用户消息发送到 AnythingLLM 的通用工作空间聊天 API (`.../workspace/{workspace_slug}/chat`)，进行无状态的单轮对话。
   - AnythingLLM 执行:
     - (对于线程化聊天) 加载指定线程的上下文。
     - 将用户问题转为向量。
     - 在向量数据库中搜索相似内容。
     - 结合检索内容、System Prompt (以及线程上下文) 生成回复。
   - 回复返回给后端，再转发到前端。

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
4. **高级会话管理**:
    - **已初步实现**: 通过 `session_id` 和 `anythingllm_thread_id` 实现了后端对 AnythingLLM 聊天线程的关联。
    - **待增强**: 前端UI支持会话列表、切换、重命名；更完善的会话超时和清理机制；后端支持列出用户会话等。
5. **高级检索**: 探索 HyDE (Hypothetical Document Embeddings) 等技术

## 参考资源

1. [AnythingLLM 官方文档](https://github.com/Mintplex-Labs/anything-llm)
2. [AnythingLLM API 文档](https://docs.anythingllm.com/api-reference/introduction)
3. [DeepSeek API 文档](https://platform.deepseek.com/docs)
4. [RAG 实现最佳实践](https://www.pinecone.io/learn/retrieval-augmented-generation/)
