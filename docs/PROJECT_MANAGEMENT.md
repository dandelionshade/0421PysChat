# PsyChat 项目管理文档

本文档整合了 PsyChat 项目的项目管理信息，包括开发计划、当前状态和优化记录，为项目团队提供统一的管理参考。

**文档最后更新**: 2025-05-15

---

# 第一部分：项目概述与规划

## 1. 项目基本信息

| 项目名称 | PsyChat (心理助手) |
| --- | --- |
| 开始日期 | 2025-04-01 |
| 预计完成日期 | 2025-07-01 |
| 项目负责人 | [项目负责人姓名] |
| 核心团队成员 | [团队成员列表] |
| 代码仓库 | [仓库地址] |
| 项目文档 | [文档地址] |
| 当前版本 | v0.1.0-alpha |
| 开发阶段 | 原型开发阶段 |

## 2. 当前项目状态

### 2.1 已完成组件

- **架构设计**
  - 建立了前后端分离架构
  - 选择了 RAG 技术路线并采用 AnythingLLM 作为 RAG 引擎
  - 完成了架构文档 (详见 `TECHNICAL_DOCUMENTATION.md`)

- **前端开发**
  - 确立了 Vue 3 + Element Plus 技术栈
  - 实现了基本 UI 布局和导航
  - 创建了聊天页面 (ChatView.vue) 和资源页面 (ResourcePage.vue)
  - 实现了与后端 API 的基本交互

- **后端开发**
  - 搭建了 FastAPI 框架
  - 实现了 `/api/chat` 和 `/api/resources` 端点
  - 设计并实现了与 AnythingLLM 的集成

- **文档**
  - 编写了详细的 RAG 实现指南
  - 更新了项目 README.md
  - 记录了项目优化和清理操作

- **数据库设置和初始化**
  - 创建了数据库模式
  - 编写了表创建 SQL
  - 准备了示例数据

### 2.2 当前进度比例

```
[=========>        ] 45% 完成
```

#### 进度明细（关键里程碑）

| 里程碑 | 状态 | 完成比例 | 预计完成时间 |
| --- | --- | --- | --- |
| 架构设计 | 已完成 | 100% | 已完成 |
| 环境搭建 | 已完成 | 100% | 已完成 |
| 数据库设计与初始化 | 已完成 | 100% | 已完成 |
| RAG 集成实现 | 部分完成 | 80% | 2025-05-20 |
| 前端基础 UI | 部分完成 | 70% | 2025-05-22 |
| 后端 API | 部分完成 | 60% | 2025-05-25 |
| 会话管理功能 | 开始实现 | 30% | 2025-06-05 |
| 用户反馈功能 | 尚未开始 | 0% | 2025-06-15 |
| 测试与优化 | 尚未开始 | 0% | 2025-06-25 |
| 部署方案实现 | 尚未开始 | 0% | 2025-06-30 |

## 3. 待完成工作

### 3.1 高优先级

1. **后端 API 增强（已完成）**
   - 实现环境变量配置（通过 `.env` 和 `os.getenv` 实现）
   - 完成 AnythingLLM 集成（核心聊天功能已连接，使用 `/api/v1/workspace/{slug}/chat` 端点，请求/响应处理已改进）
   - 错误处理机制（已增强，包括 `HTTPStatusError`、`RequestError` 和一般异常捕获，并添加了日志记录）

2. **线程化聊天稳定性提升（进行中）**
   - 实现会话超时和自动清理机制
   - 增强错误处理，确保异常情况下的会话持久性
   - 实现会话恢复机制
   - **目标完成日期**: 2025-05-25
   - **负责人**: [开发者姓名]

### 3.2 中优先级

3. **用户反馈功能**
   - 在前端添加反馈 UI 组件
   - 在后端实现 `/api/feedback` 端点
   - 存储和分析反馈数据
   - 设计反馈报告界面
   - **目标完成日期**: 2025-06-15
   - **负责人**: [开发者姓名]

4. **聊天历史功能**
   - 设计会话存储模型
   - 实现会话保存和加载 API
   - 实现前端历史记录 UI
   - 增加会话管理功能（重命名、删除等）
   - **目标完成日期**: 2025-06-05
   - **负责人**: [开发者姓名]

5. **测试用例开发**
   - 单元测试 (后端每个端点，前端每个组件)
   - 集成测试 (前后端交互)
   - 端到端测试 (用户场景测试)
   - 性能测试 (负载测试和响应时间测试)
   - **目标完成日期**: 2025-06-25
   - **负责人**: [测试负责人姓名]

### 3.3 低优先级

6. **RAG 模型与知识库优化**
   - **文档分块策略优化**
     - 当前: 标准 AnythingLLM 512 token 分块，150 token 重叠
     - 目标: 测试不同分块大小 (256-1024 tokens) 和重叠率 (10%-30%)，针对中文心理健康文本特点优化
     - 评估指标: 检索相关性分数提升 15%+，用户满意度提升 20%+
   
   - **中文心理健康领域嵌入模型评估**
     - 当前: bge-base-zh-v1.5 
     - 候选模型: 
       - bge-large-zh-v1.5 (更大，可能更精确但资源消耗更高)
       - text2vec-large-chinese (专为中文优化)
       - m3e-large (多语言支持，中文表现良好)
     - 评估方法: 创建心理健康领域测试集，比较相似度搜索准确率和检索质量
   
   - **知识库扩充与质量提升**
     - 当前容量: ~200 文档，主要为基础心理健康知识
     - 目标扩充: 
       - 增加专业心理学教材摘录 (重点: CBT, DBT, 危机干预)
       - 添加中国本土心理健康研究资料 
       - 纳入最新心理健康指南和实践标准
       - 建立分层知识体系 (基础知识、专业知识、应用指导)
     - 质量控制: 建立审核流程，确保所有资料符合专业标准和准确性
   
   - **RAG 提示词工程优化**
     - 实施提示词模板化，创建针对不同心理健康主题的专用提示词
     - 增强上下文窗口设计，更好地组织检索内容
     - 设计更精确的相关性权重策略，减少知识幻觉
     - 添加中文特定的提示词增强（考虑语言特性和表达习惯）
   
   - **检索算法优化**
     - 测试与实施混合检索策略 (结合关键词和语义检索)
     - 评估 HyDE (Hypothetical Document Embeddings) 在心理健康问题上的效果
     - 实现检索结果再排序机制，提高最相关内容优先级
     - 添加元数据过滤功能，根据问题类型智能调整检索范围
   
   - **目标完成日期**: 2025-07-30
   - **负责人**: [AI 工程师姓名] + [心理专业顾问姓名]
   - **成功指标**: 
     - 检索准确率提升 25%
     - 用户满意度提升 30%
     - 减少 40% 的无效或错误回应
     - 领域特定问题回答质量提升 50%

7. **性能优化**
   - **响应速度优化**
     - 前端优化:
       - 实现渐进式加载和流式响应显示
       - 优化组件渲染策略，减少不必要的重绘
       - 实现请求节流和智能缓存策略
       - 目标: 首屏加载时间 < 1.5s，响应显示延迟 < 300ms
     
     - 后端优化:
       - 优化 FastAPI 路由和依赖注入
       - 实现请求队列管理和优先级处理
       - 优化与 AnythingLLM 的通信协议和数据传输
       - 实现高效的数据库连接池和查询优化
       - 目标: API 平均响应时间 < 500ms，P95 < 2s
   
   - **资源使用优化**
     - 内存占用优化:
       - 实现 AnythingLLM 资源动态分配
       - 优化向量数据库索引和存储结构
       - 实现智能会话清理和资源回收
       - 目标: 平均内存占用减少 30%，峰值占用减少 25%
     
     - 计算资源优化:
       - 实现模型推理批处理
       - 优化嵌入计算过程
       - 实现检索任务并行化
       - 目标: CPU 利用率优化 20%，处理相同请求数量的资源减少 30%
   
   - **缓存策略实现**
     - 设计多层缓存架构:
       - 前端本地缓存 (常用资源和UI元素)
       - API 响应缓存 (常见问题的标准回答)
       - 向量检索结果缓存 (热门话题相关文档)
       - 会话上下文智能缓存 (减少重复处理)
     - 缓存失效策略:
       - 实现基于时间和内容更新的缓存失效机制
       - 优先级缓存替换算法
     - 目标: 热门查询响应时间减少 70%，整体系统吞吐量提升 50%
   
   - **目标完成日期**: 2025-08-15
   - **负责人**: [后端工程师姓名] + [前端工程师姓名] + [性能优化专家姓名]
   - **成功指标**:
     - 系统整体响应时间减少 40%
     - 资源利用效率提升 30%
     - 支持并发用户数从 100 提升至 500 
     - 系统稳定性指标提升 (可用性从 99% 提升至 99.9%)

## 4. 具体开发步骤

### 4.1 数据库初始化与扩展

1. 创建数据库模式：

```sql
CREATE DATABASE IF NOT EXISTS psychat CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE psychat;
```

2. 创建资源表：

```sql
CREATE TABLE IF NOT EXISTS resources (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  category VARCHAR(50),
  location_tag VARCHAR(50),
  contact_info VARCHAR(255),
  url VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  active BOOLEAN DEFAULT TRUE
);
```

3. 创建会话管理表：

```sql
CREATE TABLE IF NOT EXISTS chat_sessions (
  id VARCHAR(36) PRIMARY KEY,
  anythingllm_thread_id VARCHAR(255),
  name VARCHAR(100) DEFAULT '新对话',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  message_count INT DEFAULT 0,
  user_id VARCHAR(36) DEFAULT NULL,
  session_data JSON DEFAULT NULL,
  INDEX idx_anythingllm_thread_id (anythingllm_thread_id),
  INDEX idx_user_id (user_id),
  INDEX idx_last_message_at (last_message_at)
);
```

4. 创建用户反馈表：

```sql
CREATE TABLE IF NOT EXISTS feedback (
  id INT AUTO_INCREMENT PRIMARY KEY,
  message_id VARCHAR(36) NOT NULL,
  session_id VARCHAR(36),
  user_query TEXT NOT NULL,
  bot_response TEXT NOT NULL,
  rating TINYINT,
  comment TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_session_id (session_id),
  INDEX idx_rating (rating)
);
```

### 4.2 用户反馈功能实现

1. 前端组件：

```vue
<!-- 添加到 ChatView.vue 消息组件 -->
<div class="message-feedback" v-if="message.role === 'assistant'">
  <el-button-group size="small">
    <el-button @click="sendFeedback(message.id, 'positive')" type="success" icon="Thumb-up" circle></el-button>
    <el-button @click="sendFeedback(message.id, 'negative')" type="danger" icon="Thumb-down" circle></el-button>
    <el-button @click="openFeedbackDialog(message.id)" plain icon="ChatDotRound"></el-button>
  </el-button-group>
  
  <!-- 详细反馈对话框 -->
  <el-dialog
    v-model="feedbackDialogVisible"
    title="提供详细反馈"
    width="50%">
    <el-form :model="feedbackForm" label-width="120px">
      <el-form-item label="满意度">
        <el-rate v-model="feedbackForm.rating" :max="5" />
      </el-form-item>
      <el-form-item label="详细反馈">
        <el-input
          type="textarea"
          v-model="feedbackForm.comment"
          :rows="4"
          placeholder="请告诉我们您的想法，帮助我们改进服务..." />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="feedbackDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitDetailedFeedback">提交</el-button>
      </span>
    </template>
  </el-dialog>
</div>

<script>
// ...existing code...

data() {
  return {
    // ...existing code...
    feedbackDialogVisible: false,
    feedbackForm: {
      messageId: null,
      rating: 3,
      comment: ''
    }
  };
},

methods: {
  async sendFeedback(messageId, rating) {
    try {
      await axios.post('/api/feedback', {
        message_id: messageId,
        session_id: this.sessionId,
        rating: rating === 'positive' ? 1 : 0,
        user_query: this.getMessageQuery(messageId),
        bot_response: this.getMessageContent(messageId)
      });
      this.$message.success('感谢您的反馈!');
    } catch (error) {
      console.error('提交反馈失败:', error);
      this.$message.error('提交反馈失败');
    }
  },
  
  openFeedbackDialog(messageId) {
    this.feedbackForm.messageId = messageId;
    this.feedbackDialogVisible = true;
  },
  
  async submitDetailedFeedback() {
    try {
      await axios.post('/api/feedback/detailed', {
        message_id: this.feedbackForm.messageId,
        session_id: this.sessionId,
        rating: this.feedbackForm.rating,
        comment: this.feedbackForm.comment,
        user_query: this.getMessageQuery(this.feedbackForm.messageId),
        bot_response: this.getMessageContent(this.feedbackForm.messageId)
      });
      this.$message.success('感谢您提供的详细反馈!');
      this.feedbackDialogVisible = false;
    } catch (error) {
      console.error('提交详细反馈失败:', error);
      this.$message.error('提交详细反馈失败');
    }
  }
}
</script>
```

2. 后端 API：

```python
# 添加到后端 main.py 或单独的 feedback_router.py
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends

class FeedbackRequest(BaseModel):
    message_id: str
    session_id: Optional[str] = None
    rating: int  # 1 表示积极，0 表示消极
    user_query: str
    bot_response: str
    comment: Optional[str] = None

class DetailedFeedbackRequest(BaseModel):
    message_id: str
    session_id: Optional[str] = None
    rating: int  # 1-5 星评分
    comment: str
    user_query: str
    bot_response: str

feedback_router = APIRouter(prefix="/api/feedback", tags=["feedback"])

@feedback_router.post("")
async def submit_feedback(request: FeedbackRequest, db = Depends(get_db)):
    try:
        query = """
        INSERT INTO feedback (message_id, session_id, user_query, bot_response, rating)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        await db.execute(
            query,
            (
                request.message_id,
                request.session_id,
                request.user_query,
                request.bot_response,
                request.rating
            )
        )
        
        # 记录反馈事件
        logger.info(f"收到反馈: message_id={request.message_id}, rating={request.rating}")
        
        return {"status": "success", "message": "反馈已记录"}
    except Exception as e:
        logger.error(f"记录反馈时出错: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="内部服务器错误")

@feedback_router.post("/detailed")
async def submit_detailed_feedback(request: DetailedFeedbackRequest, db = Depends(get_db)):
    try:
        query = """
        INSERT INTO feedback (message_id, session_id, user_query, bot_response, rating, comment)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        await db.execute(
            query,
            (
                request.message_id,
                request.session_id,
                request.user_query,
                request.bot_response,
                request.rating,
                request.comment
            )
        )
        
        # 记录详细反馈事件
        logger.info(f"收到详细反馈: message_id={request.message_id}, rating={request.rating}, comment_length={len(request.comment)}")
        
        return {"status": "success", "message": "详细反馈已记录"}
    except Exception as e:
        logger.error(f"记录详细反馈时出错: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="内部服务器错误")

# 在主应用中引入该路由
# app.include_router(feedback_router)
```

## 5. 测试策略

### 5.1 测试类型和范围

| 测试类型 | 目标 | 工具 | 负责人 |
| --- | --- | --- | --- |
| 单元测试 | 确保各组件按预期工作 | PyTest, Vue Test Utils | [开发团队] |
| 集成测试 | 验证组件间交互正常 | PyTest | [测试团队] |
| 端到端测试 | 验证完整用户流程 | Cypress | [测试团队] |
| 性能测试 | 确保在预期负载下性能可接受 | Locust | [运维团队] |
| 安全测试 | 识别潜在安全漏洞 | OWASP ZAP | [安全团队] |

### 5.2 具体测试计划

1. **单元测试**:
   - 后端端点测试（全部 API 路由）
   - 前端组件测试（特别是聊天和资源组件）
   - 工具函数测试
   - 目标覆盖率: >80%

2. **集成测试**:
   - 前端-后端通信测试
   - 后端-AnythingLLM 通信测试
   - 数据库操作测试
   - 会话管理功能测试

3. **端到端测试**:
   - 用户聊天场景测试
   - 资源查询场景测试
   - 会话管理场景测试
   - 长对话测试
   - 极端用例测试（非常长的输入、特殊字符等）

4. **性能测试**:
   - 并发用户测试（目标: 支持 100 并发用户）
   - 长时间稳定性测试（24小时连续运行）
   - 响应时间测试（目标: P95 < 2秒）

## 6. 部署规划

### 6.1 部署环境

| 环境 | 用途 | 服务器配置 | 访问地址 |
| --- | --- | --- | --- |
| 开发环境 | 开发和单元测试 | 本地机器 | localhost |
| 测试环境 | 集成和性能测试 | 2核4G云服务器 | test.psychat.example.com |
| 预发布环境 | 验收测试 | 4核8G云服务器 | staging.psychat.example.com |
| 生产环境 | 正式服务 | 8核16G云服务器 | psychat.example.com |

### 6.2 部署流程

1. 准备环境：
   - 安装 Docker 和 Docker Compose
   - 配置网络和存储
   - 设置监控和日志收集

2. Docker Compose 配置：

```yaml
# docker-compose.yml 示例
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      args:
        - API_BASE_URL=${API_BASE_URL}
    image: psychat-frontend:${TAG:-latest}
    ports:
      - "${FRONTEND_PORT:-80}:80"
    depends_on:
      - backend
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:80"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - psychat-network
      
  backend:
    build: ./backend
    image: psychat-backend:${TAG:-latest}
    ports:
      - "${BACKEND_PORT:-8000}:8000"
    environment:
      - DATABASE_URL=mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@db:3306/psychat
      - ANYTHINGLLM_API_BASE_URL=http://anythingllm:3001
      - ANYTHINGLLM_WORKSPACE_SLUG=${ANYTHINGLLM_WORKSPACE_SLUG:-mentalhealthbot}
      - ANYTHINGLLM_API_KEY=${ANYTHINGLLM_API_KEY}
      - LOG_LEVEL=${LOG_LEVEL:-info}
    depends_on:
      - db
      - anythingllm
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    volumes:
      - ./logs:/app/logs
    networks:
      - psychat-network
      
  db:
    image: mysql:8.0
    ports:
      - "${MYSQL_PORT:-3306}:3306"
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
      - MYSQL_DATABASE=psychat
      - MYSQL_USER=${MYSQL_USER}
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
    volumes:
      - mysql-data:/var/lib/mysql
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
      - ./database/backup:/backup
    restart: unless-stopped
    command: --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p${MYSQL_ROOT_PASSWORD}"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - psychat-network
      
  anythingllm:
    image: mintplexlabs/anythingllm:${ANYTHINGLLM_VERSION:-latest}
    ports:
      - "${ANYTHINGLLM_PORT:-3001}:3001"
    volumes:
      - anythingllm-data:/app/server/storage
    environment:
      - LLM_PROVIDER=custom
      - CUSTOM_MODEL_URL=${DEEPSEEK_API_URL}
      - CUSTOM_MODEL_KEY=${DEEPSEEK_API_KEY}
      - EMBEDDING_ENGINE=${EMBEDDING_ENGINE:-bge-base-zh-v1.5}
      - AUTH_TOKEN=${ANYTHINGLLM_AUTH_TOKEN}
      - STORAGE_DIR=/app/server/storage
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3001/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - psychat-network

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - psychat-network

  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin}
    networks:
      - psychat-network

networks:
  psychat-network:

volumes:
  mysql-data:
  anythingllm-data:
  prometheus-data:
  grafana-data:
```

### 6.3 持续集成/持续部署 (CI/CD)

使用 GitHub Actions 或 GitLab CI 实现以下流程：

1. **代码提交触发**:
   - 运行 linting
   - 运行单元测试
   - 构建 Docker 镜像

2. **合并到开发分支**:
   - 部署到测试环境
   - 运行集成测试

3. **合并到主分支**:
   - 部署到预发布环境
   - 运行端到端测试
   - 生成版本标签

4. **创建发布标签**:
   - 部署到生产环境
   - 运行生产健康检查

## 7. 项目时间线

![项目甘特图](./images/project_timeline.png)

### 7.1 主要里程碑

| 里程碑 | 预计完成日期 | 状态 |
| --- | --- | --- |
| 项目启动 | 2025-04-01 | 已完成 |
| 架构设计完成 | 2025-04-15 | 已完成 |
| 原型版本发布 | 2025-05-15 | 进行中 |
| 测试版本发布 | 2025-06-15 | 计划中 |
| 公测版本发布 | 2025-06-30 | 计划中 |
| 正式版发布 | 2025-07-15 | 计划中 |

### 7.2 周进度计划

#### 当前周 (2025-05-15 至 2025-05-21)

- [ ] 完成会话管理功能核心实现
- [ ] 解决前端聊天界面已知问题
- [ ] 优化 AnythingLLM 与后端的集成
- [ ] 增加系统级日志记录
- [ ] 实现会话恢复机制

#### 下周 (2025-05-22 至 2025-05-28)

- [ ] 提高 API 错误处理鲁棒性
- [ ] 开始用户反馈功能前端实现
- [ ] 设计并实现用户反馈分析工具
- [ ] 增加系统监控指标收集
- [ ] 开始单元测试编写

## 8. 问题与风险管理

| 风险 | 可能性 | 影响 | 缓解策略 | 负责人 |
| --- | --- | --- | --- | --- |
| 知识库质量不足 | 高 | 高 | 扩充并精选专业心理健康文档，建立内容审核流程 | 内容团队 |
| LLM模型回答不当 | 中 | 高 | 优化提示词工程，增加安全过滤机制，建立人工审核流程 | 技术团队 |
| 系统性能瓶颈 | 中 | 中 | 进行性能测试与监控，优化查询和缓存策略 | 开发团队 |
| API接口不稳定 | 中 | 高 | 增加错误重试机制，优化故障恢复 | 开发团队 |
| 数据隐私风险 | 低 | 高 | 实施严格的数据加密和匿名化，明确隐私政策 | 安全团队 |

### 8.1 当前关键问题追踪

| 问题ID | 问题描述 | 优先级 | 状态 | 负责人 | 目标解决日期 |
| --- | --- | --- | --- | --- | --- |
| IS-001 | 聊天会话在页面刷新后丢失 | 高 | 解决中 | 前端开发 | 2025-05-20 |
| IS-002 | RAG 回答中存在中文语法错误 | 中 | 解决中 | 提示词工程师 | 2025-05-22 |
| IS-003 | 在高并发下数据库连接超时 | 高 | 待解决 | 后端开发 | 2025-05-25 |
| IS-004 | AnythingLLM 嵌入模型对专业术语效果不佳 | 中 | 调查中 | RAG专家 | 待定 |

---

# 第二部分：项目优化记录

## 1. 代码与架构优化 (2025-05-10)

### 1.1 冗余文件清理

以下文件被识别为冗余或过时，建议删除：

- **`./main.py`**:
  - **原因**: 此文件位于项目根目录，似乎是 `backend/main.py` 的早期版本或测试版本。它使用 SQLite 而非项目当前使用的 MySQL，并且包含与当前后端实现不一致的代码逻辑。
  - **处理状态**: 已删除 ✓

- **`./docs/DEVELOPMENT.md`**:
  - **原因**: 此开发文档描述了基于 Node.js/Express.js 的后端和 `client/`、`server/` 的目录结构，这与项目当前使用的 Python/FastAPI 后端和 `frontend/`、`backend/` 结构不一致。文档内容已过时，可能导致混淆。当前架构更准确地由 `TECHNICAL_DOCUMENTATION.md` 描述。
  - **处理状态**: 已删除 ✓

### 1.2 版本控制优化

- **操作**: 在项目根目录的 `.gitignore` 文件中添加了 `.idea/`、`__pycache__/`、`*.pyc`、`*.pyo`、`*.pyd`。
- **原因**: 这是忽略 IDE 配置文件和 Python 编译文件的标准做法，有助于保持仓库清洁并避免不同开发者之间因 IDE 配置差异而产生冲突。
- **处理状态**: 已完成 ✓

### 1.3 文档体系优化

- **操作**: 重新组织文档结构，建立了清晰的文档层次关系：
  - `README.md`: 项目总览，入口文档
  - `TECHNICAL_DOCUMENTATION.md`: 技术实现与架构文档
  - `PROJECT_MANAGEMENT.md`: 项目管理与进度文档
  - 将过时文档移至 `docs/Archives/` 目录
- **处理状态**: 已完成 ✓

### 1.4 前端环境优化

- **目的**: 优化前端开发体验，提高构建效率。
- **操作**:
  - 升级 Vite 版本到 4.3.9
  - 新增 ESLint 和 Prettier 配置
  - 添加预提交钩子，确保代码质量
  - 优化构建配置，减少生产包大小
- **处理状态**: 已完成 ✓

### 1.5 项目结构标准化

- **目的**: 使项目结构符合标准化要求，优化文件组织，提高开发效率和可维护性。
- **具体变更**:

#### 实施标准文件结构

确保项目符合以下标准化的文件结构：

```
.
├── backend          # 后端代码
│   ├── api          # API 定义 (包含 Pydantic 模型或 OpenAPI schema)
│   ├── core         # 核心配置、设置、通用工具
│   ├── db           # 数据库连接、模型 (如 SQLAlchemy 模型)
│   ├── models       # Pydantic 请求/响应模型
│   ├── routers      # API 路由 (FastAPI routers)
│   ├── services     # 业务逻辑服务层
│   ├── tests        # 后端测试文件
│   └── main.py      # FastAPI 应用入口
├── database         # 数据库相关文件
│   ├── migrations   # 数据库迁移脚本
│   └── init.sql     # 初始化SQL脚本
├── docs             # 项目文档
│   ├── images       # 文档中使用的图片
│   ├── Archives     # 归档的旧文档
│   └── *.md         # 各种文档文件
├── frontend         # 前端代码
│   ├── public       # 静态资源 (如 index.html, favicons)
│   └── src          # Vue 应用源码
│       ├── assets   # 静态资源 (图片, 字体等)
│       ├── components # Vue 组件
│       ├── composables # Vue 组合式函数
│       ├── router    # Vue Router 配置
│       ├── services  # API 服务和数据处理
│       ├── stores    # 状态管理
│       ├── views     # Vue 页面视图
│       └── App.vue   # Vue 应用根组件
├── monitoring       # 监控和日志配置
├── scripts          # 自动化脚本
│   ├── deploy.sh    # 部署脚本
│   └── setup.sh     # 环境设置脚本
├── .env.example     # 环境变量示例
├── .gitignore       # Git 忽略配置
├── docker-compose.yml # Docker 配置
└── README.md        # 项目说明文件
```

- **处理状态**: 部分完成，持续优化中

## 2. 功能优化记录

### 2.1 线程化聊天支持 (2025-05-08)

- **变更内容**:
  - **后端 (`main.py`)**:
    - `ChatRequest` 模型已更新，包含可选的 `session_id`。
    - `/api/chat` 端点逻辑已增强以处理 `session_id`。
    - 实现了与 AnythingLLM 线程 API 的集成。
  - **数据库**:
    - 增加了 `chat_sessions` 表及相关索引。
- **优化效果**: 
  - 实现了对话上下文的持久化存储
  - 改善了多轮对话的连贯性和相关性
  - 支持同一用户管理多个独立的对话线程
- **处理状态**: 已完成基础功能 ✓，需进一步稳定性增强

### 2.2 错误处理增强 (2025-05-12)

- **变更内容**:
  - 引入全局异常处理中间件
  - 增加详细日志记录
  - 实现请求重试机制
  - 规范化错误响应格式
- **优化效果**:
  - 提高系统稳定性
  - 改善用户错误提示体验
  - 增强问题诊断能力
- **处理状态**: 已完成 ✓

## 3. 性能优化记录

### 3.1 数据库查询优化 (2025-05-14)

- **变更内容**:
  - 为频繁查询的字段添加索引
  - 优化 SQL 查询语句
  - 实现连接池管理
- **优化效果**:
  - 查询响应时间减少 60%
  - 减轻数据库负载
- **处理状态**: 已完成 ✓

### 3.2 前端性能优化 (进行中)

- **变更内容**:
  - 实现组件懒加载
  - 优化资源加载策略
  - 改进状态管理
- **预期效果**:
  - 首屏加载时间缩短
  - 页面交互更流畅
- **处理状态**: 进行中

## 总结

本次优化工作大幅改进了项目结构、功能和性能，为后续开发奠定了更加规范和稳定的基础。仍有部分优化工作在进行中，将在后续更新中继续改进。
