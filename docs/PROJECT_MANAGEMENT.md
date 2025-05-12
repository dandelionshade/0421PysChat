# PsyChat Project Management Documentation

This document consolidates project management information for PsyChat, including development plans, current status, and optimization records.

---

# Part 1: Development Plan

## 1. Current Project Status

### Completed Components

- **Architecture Design**
  - Established front-end/back-end separation architecture
  - Selected RAG technology route and adopted AnythingLLM as RAG engine
  - Completed architecture documentation (RAG_IMPLEMENTATION.md)

- **Frontend Development**
  - Established Vue 3 + Element Plus technology stack
  - Implemented basic UI layout and navigation
  - Created chat page (ChatView.vue) and resource page (ResourcePage.vue)
  - Implemented basic interaction with backend API

- **Backend Development**
  - Set up FastAPI framework
  - Implemented /api/chat and /api/resources endpoints
  - Designed integration plan with AnythingLLM

- **Documentation**
  - Wrote detailed RAG implementation guide
  - Updated project README.md
  - Recorded project optimizations and cleanup operations

- **Database Setup and Initialization**
  - Created database schema
  - Wrote table creation SQL
  - Prepared example data

## 2. Pending Work

### 2.1 High Priority

1. **Backend API Enhancement (Completed)**
   - Implement environment variable configuration (Achieved through `.env` and `os.getenv`)
   - Complete AnythingLLM integration (Core chat functionality connected, using `/api/v1/workspace/{slug}/chat` endpoint, with request/response handling improved)
   - Error handling mechanism (Enhanced, including `HTTPStatusError`, `RequestError` and general exception catching, with logging added)

### 2.2 Medium Priority

2. **User Feedback Feature**
   - Add feedback UI components to frontend
   - Implement /api/feedback endpoint on backend
   - Store and analyze feedback data

3. **Chat History Feature**
   - Design session storage model
   - Implement session save and load API
   - Frontend history record UI

4. **Test Case Development**
   - Unit tests
   - Integration tests
   - End-to-end tests

### 2.3 Low Priority

5. **AnythingLLM Configuration and Knowledge Base Optimization (Initially completed, retained for future optimization)**
   - Install and configure AnythingLLM (Completed)
   - Prepare mental health knowledge documents (Completed)
   - Test RAG effects (Completed)

6. **Performance Optimization**
   - Response speed optimization
   - Resource usage optimization
   - Caching strategy

7. **Deployment Plan**
   - Docker containerization
   - CI/CD process
   - Monitoring solution

## 3. Specific Development Steps

### 3.1 Database Initialization

1. Create database schema:

```sql
CREATE DATABASE IF NOT EXISTS psychat CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE psychat;
```

2. Create resources table:

```sql
CREATE TABLE IF NOT EXISTS resources (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  category VARCHAR(50),
  location_tag VARCHAR(50),
  contact_info VARCHAR(255),
  url VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

3. Add example data:

```sql
INSERT INTO resources (title, description, category, location_tag, contact_info, url)
VALUES 
('全国心理援助热线', '提供24小时心理支持和危机干预', 'crisis', 'national', '400-161-9995', 'https://example.com/hotline'),
('心理健康咨询中心', '提供专业心理咨询服务', 'counseling', 'beijing', '010-12345678', 'https://example.com/center'),
('抑郁症自助小组', '抑郁症患者互助社区', 'support', 'online', 'depression@example.com', 'https://example.com/depression'),
('冥想与放松技巧课程', '学习减压和情绪管理技巧', 'self-help', 'shanghai', '021-87654321', 'https://example.com/meditation'),
('心理健康公益讲座', '免费心理健康教育', 'education', 'guangzhou', 'lectures@example.com', 'https://example.com/lectures');
```

4. (Optional) Create user feedback table:

```sql
CREATE TABLE IF NOT EXISTS feedback (
  id INT AUTO_INCREMENT PRIMARY KEY,
  message_id VARCHAR(36) NOT NULL,
  user_query TEXT NOT NULL,
  bot_response TEXT NOT NULL,
  rating TINYINT,
  comment TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 AnythingLLM Configuration

1. Download and install AnythingLLM Desktop application
2. Configure LLM Provider:
   - Go to Settings → LLM Provider
   - Select "OpenAI-compatible URL"
   - Enter DeepSeek API URL and API Key
   - Select model and test connection

3. Configure Embedding model:
   - Go to Settings → Embedding Engine
   - Select Chinese model like "bge-base-zh-v1.5"

4. Create Workspace:
   - Create workspace named "MentalHealthBot"
   - Set System Prompt (see detailed prompt below):

```
你是一位专业、善解人意的心理健康顾问，名为"心理助手"。你的职责是提供情感支持和基于证据的心理健康信息。基于你的知识库，你应提供准确、科学的回应，并在必要时推荐专业资源。在危机情况下，你会提供紧急联系方式，如全国心理援助热线: 400-161-9995。请保持温暖且专业的语气，不作出诊断或治疗建议，而是引导用户寻求适当的专业帮助。
```

For detailed System Prompt, refer to the `TECHNICAL_DOCUMENTATION.md` file

5. Prepare knowledge documents:
   - Collect mental health resource documents (textbook excerpts, articles, FAQs, etc.)
   - Save as txt or pdf format
   
6. Upload documents to AnythingLLM:
   - Upload documents through AnythingLLM interface
   - Observe document processing progress
   - Test RAG effects

### 3.3 User Feedback Feature Implementation

1. Frontend component:

```vue
<!-- Add to ChatView.vue message component -->
<div class="message-feedback" v-if="message.role === 'assistant'">
  <el-button-group size="small">
    <el-button @click="sendFeedback(message.id, 'positive')" type="success" icon="Thumb-up" circle></el-button>
    <el-button @click="sendFeedback(message.id, 'negative')" type="danger" icon="Thumb-down" circle></el-button>
  </el-button-group>
</div>

<script>
methods: {
  async sendFeedback(messageId, rating) {
    try {
      await axios.post('/api/feedback', {
        message_id: messageId,
        rating: rating === 'positive' ? 1 : 0,
        user_query: this.getMessageQuery(messageId),
        bot_response: this.getMessageContent(messageId)
      });
      this.$message.success('感谢您的反馈!');
    } catch (error) {
      console.error('提交反馈失败:', error);
      this.$message.error('提交反馈失败');
    }
  }
}
</script>
```

2. Backend API:

```python
# Add to backend main.py
from pydantic import BaseModel
from uuid import UUID

class FeedbackRequest(BaseModel):
    message_id: str
    rating: int  # 1 for positive, 0 for negative
    user_query: str
    bot_response: str
    comment: str = None

@app.post("/api/feedback")
async def submit_feedback(request: FeedbackRequest):
    try:
        query = """
        INSERT INTO feedback (message_id, user_query, bot_response, rating, comment)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        await database.execute(
            query,
            (
                request.message_id,
                request.user_query,
                request.bot_response,
                request.rating,
                request.comment
            )
        )
        
        return {"status": "success", "message": "Feedback recorded"}
    except Exception as e:
        logger.error(f"Error recording feedback: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

## 4. Testing Plan

1. Unit Tests:
   - Test backend API endpoints
   - Test frontend component functionality

2. Integration Tests:
   - Test frontend-backend interaction
   - Test interaction with AnythingLLM

3. User Testing:
   - Collect user feedback
   - Analyze chat logs and common issues

## 5. Deployment Planning

1. Prepare environment:
   - Install Docker and Docker Compose
   - Configure network and storage

2. Prepare Docker configuration:

```yaml
# docker-compose.yml example
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
      
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql+pymysql://user:password@db:3306/psychat
      - ANYTHINGLLM_API_BASE_URL=http://anythingllm:3001
      - ANYTHINGLLM_WORKSPACE_SLUG=mentalhealthbot
      - ANYTHINGLLM_API_KEY=${ANYTHINGLLM_API_KEY}
    depends_on:
      - db
      - anythingllm
      
  db:
    image: mysql:8.0
    ports:
      - "3306:3306"
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
      - MYSQL_DATABASE=psychat
      - MYSQL_USER=${MYSQL_USER}
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
    volumes:
      - mysql-data:/var/lib/mysql
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
      
  anythingllm:
    image: mintplexlabs/anythingllm:latest
    ports:
      - "3001:3001"
    volumes:
      - anythingllm-data:/app/server/storage
    environment:
      - LLM_PROVIDER=custom
      - CUSTOM_MODEL_URL=${DEEPSEEK_API_URL}
      - CUSTOM_MODEL_KEY=${DEEPSEEK_API_KEY}
      - EMBEDDING_ENGINE=bge-base-zh-v1.5

volumes:
  mysql-data:
  anythingllm-data:
```

## 6. Recommended Project Timeline

- **Phase 1** (1-2 weeks): 
  - Complete database setup
  - Configure AnythingLLM
  - Adjust backend API

- **Phase 2** (2-3 weeks):
  - Implement user feedback feature
  - Develop chat history feature
  - Write tests

- **Phase 3** (1-2 weeks):
  - Perform performance optimization
  - Prepare deployment plan
  - User testing and adjustments

## 7. Issues and Risks

1. **Knowledge Base Quality**: The quality and coverage of mental health knowledge documents will directly affect RAG effectiveness
2. **Model Selection**: Need to select LLM and embedding models suitable for Chinese mental health domain
3. **Resource Consumption**: AnythingLLM will occupy substantial system resources, requiring appropriate server configuration
4. **Privacy and Security**: Mental health data is sensitive, requiring strengthened data protection measures

---

# Part 2: Project Optimizations Record (2025-05-10)

This section records structure optimizations and file cleanup operations performed on the PsyChat project.

## 1. Redundant File Cleanup

The following files were identified as redundant or outdated and recommended for deletion:

* **`# main.py`**:
  * **Reason**: This file is located in the project root directory and appears to be an early or test version of `backend/main.py`. It uses SQLite instead of MySQL currently used by the project, and contains code logic inconsistent with the current backend implementation.
  * **Action**: Recommend manually deleting this file.
* **`DEVELOPMENT.md`**:
  * **Reason**: This development document describes a backend based on Node.js/Express.js and a directory structure of `client/`, `server/`, which is inconsistent with the Python/FastAPI backend and `frontend/`, `backend/` structure currently used by the project. The document content is outdated and may cause confusion. The current architecture is more accurately described by `RAG_IMPLEMENTATION.md`.
  * **Action**: Recommend manually deleting this file.

## 2. `.gitignore` Optimization

* **Action**: Added `.idea/` to the `.gitignore` file in the project root directory.
* **Reason**: This is standard practice for ignoring project configuration files automatically generated by JetBrains IDEs (such as PyCharm, IntelliJ IDEA), helping to keep the repository clean and avoid conflicts between different developers due to IDE configuration differences.

## 3. `README.md` Enhancement

* **Action**: Updated the `README.md` file.
* **Reason**: The original `README.md` file was too simple. The updated version includes project objectives, current technology stack, brief architecture description (linked to `RAG_IMPLEMENTATION.md`), and a more detailed quick start guide, making it easier for new members or future self to quickly understand and run the project.

## 4. Frontend Environment Supplement

* Purpose: Build and launch a frontend application based on Vue 3 + Vite, integrating Element Plus, providing chat and resource pages.
* Added/Modified files:
  * **frontend/package.json**: Improved project metadata, scripts, added dependencies such as `vue`, `vue-router`, `vite`, `@vitejs/plugin-vue`.
  * **frontend/index.html**: Added application entry HTML.
  * **frontend/src/App.vue**: Added main layout component, including navigation and route view.
  * **frontend/src/views/ChatView.vue**: Added chat page component, implementing message display, input, and backend API calls.
  * **frontend/src/views/ResourcePage.vue**: Added resource list page component, implementing filter form and resource display.

## 5. Project Structure Standardization (2025-05-10)

* **Purpose**: Make the project structure meet standardization requirements, optimize file organization, improve development efficiency and maintainability.
* **Specific changes**:

### 5.1 Standard File Structure Implementation

Ensured the project conforms to the following standardized file structure:

```
.
├── backend
│   ├── api
│   ├── core
│   ├── db
│   ├── models
│   ├── routers
│   ├── services
│   └── main.py
├── docs
│   ├── images
│   └── PROJECT_OPTIMIZATIONS.md
├── frontend
│   ├── public
│   └── src
│       ├── assets
│       ├── components
│       ├── views
│       └── App.vue
├── tests
│   ├── integration
│   └── unit
└── README.md
```

### 5.2 File Naming Conventions

* All Python source files use lowercase letters and underscore naming convention (e.g., `main.py`, `user_router.py`).
* All frontend files use lowercase letters and hyphen naming convention (e.g., `app.vue`, `user-profile.vue`).

### 5.3 Directory Structure Optimization

* Backend:
  * **Action**: Moved all backend Python source files to the `backend/` directory, and subdivided into subdirectories by functional module.
  * **Reason**: Unified backend code storage location, subdivided into subdirectories by functional module, helping code organization and management.
* Frontend:
  * **Action**: Moved all frontend source files to the `frontend/src/` directory, and subdivided into subdirectories by function.
  * **Reason**: Unified frontend code storage location, subdivided into subdirectories by function, helping code organization and management.

## 6. Recent Feature Enhancements (As of Latest Update)

*   **Threaded Chat Support**:
    *   **Backend (`main.py`)**:
        *   `ChatRequest` model has been updated to include an optional `session_id`.
        *   `/api/chat` endpoint logic enhanced to handle `session_id`.
        *   When a `session_id` is provided, the backend will:
            1.  Query the database (`chat_sessions` table) to retrieve the `anythingllm_thread_id` associated with the `session_id`.
            2.  If it exists, use AnythingLLM's `/v1/workspace/{slug}/thread/{thread_id}/chat` endpoint for chatting.
            3.  If it doesn't exist, call `/v1/workspace/{slug}/thread/new` to create a new thread, store the returned `threadSlug` (as `anythingllm_thread_id`) in the database, and then chat using the new thread.
        *   If no `session_id` is provided, fall back to using the generic `/v1/workspace/{slug}/chat` endpoint.
    *   **Database (`init.sql`)**:
        *   `chat_sessions` table has been added with an `anythingllm_thread_id` column to store AnythingLLM's thread identifier, and a corresponding index has been established.
    *   **Purpose**: This change allows maintaining conversation context across multiple interactions by linking PsyChat sessions to specific chat threads in AnythingLLM.

## Summary

By removing redundant files and outdated documentation, optimizing `.gitignore` configuration, and enhancing `README.md`, the project structure becomes clearer, documentation more consistent with actual code, helping subsequent development and maintenance.
