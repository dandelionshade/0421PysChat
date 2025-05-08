# PsyChat 开发规划文档

本文档总结了PsyChat项目的当前状态、未完成工作和推荐的开发步骤，旨在指导后续开发工作顺利进行。

## 1. 当前项目状态

### 已完成部分

- **架构设计**
  - 确立了前后端分离架构
  - 选择了RAG技术路线并采用AnythingLLM作为RAG引擎
  - 完成了架构文档(RAG_IMPLEMENTATION.md)

- **前端开发**
  - 建立了Vue 3 + Element Plus技术栈
  - 实现了基本UI布局和导航
  - 创建了聊天页面(ChatView.vue)和资源页面(ResourcePage.vue)
  - 实现了与后端API的基本交互

- **后端开发**
  - 搭建了FastAPI框架
  - 实现了/api/chat和/api/resources端点
  - 设计了与AnythingLLM的集成方案

- **文档编写**
  - 编写了详细的RAG实现指南
  - 更新了项目README.md
  - 记录了项目优化与清理操作

- **数据库设置与初始化**
  - 创建了数据库schema
  - 编写了表创建SQL
  - 准备了示例数据

## 2. 未完成工作

### 2.1 优先级高

1. **AnythingLLM配置与知识库构建**
   - 安装和配置AnythingLLM
   - 准备心理健康知识文档
   - 测试RAG效果

2. **后端API完善**
   - 实现环境变量配置
   - 完成AnythingLLM集成
   - 错误处理机制

### 2.2 优先级中

3. **用户反馈功能**
   - 前端添加反馈UI组件
   - 后端实现/api/feedback端点
   - 反馈数据存储和分析

4. **聊天历史功能**
   - 设计会话存储模型
   - 实现会话保存和加载API
   - 前端历史记录UI

5. **测试用例开发**
   - 单元测试
   - 集成测试
   - 端到端测试

### 2.3 优先级低

6. **性能优化**
   - 响应速度优化
   - 资源占用优化
   - 缓存策略

7. **部署方案**
   - Docker容器化
   - CI/CD流程
   - 监控方案

## 3. 具体开发步骤

### 3.1 数据库初始化

1. 创建数据库schema:

```sql
CREATE DATABASE IF NOT EXISTS psychat CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE psychat;
```

2. 创建资源表:

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

3. 添加示例数据:

```sql
INSERT INTO resources (title, description, category, location_tag, contact_info, url)
VALUES 
('全国心理援助热线', '提供24小时心理支持和危机干预', 'crisis', 'national', '400-161-9995', 'https://example.com/hotline'),
('心理健康咨询中心', '提供专业心理咨询服务', 'counseling', 'beijing', '010-12345678', 'https://example.com/center'),
('抑郁症自助小组', '抑郁症患者互助社区', 'support', 'online', 'depression@example.com', 'https://example.com/depression'),
('冥想与放松技巧课程', '学习减压和情绪管理技巧', 'self-help', 'shanghai', '021-87654321', 'https://example.com/meditation'),
('心理健康公益讲座', '免费心理健康教育', 'education', 'guangzhou', 'lectures@example.com', 'https://example.com/lectures');
```

4. (可选)创建用户反馈表:

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

### 3.2 AnythingLLM配置

1. 下载并安装AnythingLLM Desktop应用
2. 配置LLM Provider:
   - 进入Settings → LLM Provider
   - 选择"兼容OpenAI的URL"
   - 填入DeepSeek API URL和API Key
   - 选择模型并测试连接

3. 配置Embedding模型:
   - 进入Settings → Embedding Engine
   - 选择中文模型如"bge-base-zh-v1.5"

4. 创建Workspace:
   - 创建名为"MentalHealthBot"的workspace
   - 设置System Prompt(参考RAG_IMPLEMENTATION.md)

5. 准备知识文档:
   - 收集心理健康资源文档(教材摘录、文章、常见问题等)
   - 保存为txt或pdf格式
   
6. 上传文档到AnythingLLM:
   - 通过AnythingLLM界面上传文档
   - 观察文档处理进度
   - 测试RAG效果

### 3.3 用户反馈功能实现

1. 前端组件:

```vue
<!-- 添加到ChatView.vue消息组件中 -->
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

2. 后端API:

```python
# 添加到后端main.py
from pydantic import BaseModel
from uuid import UUID

class FeedbackRequest(BaseModel):
    message_id: str
    rating: int  # 1表示赞同，0表示不赞同
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
        
        return {"status": "success", "message": "反馈已记录"}
    except Exception as e:
        logger.error(f"Error recording feedback: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误")
```

## 4. 测试计划

1. 单元测试:
   - 测试后端API端点
   - 测试前端组件功能

2. 集成测试:
   - 测试前后端交互
   - 测试与AnythingLLM交互

3. 用户测试:
   - 收集用户使用反馈
   - 分析聊天日志和常见问题

## 5. 部署规划

1. 准备环境:
   - 安装Docker和Docker Compose
   - 配置网络和存储

2. 准备Docker配置:

```yaml
# docker-compose.yml示例
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

## 6. 项目时间线建议

- **阶段1** (1-2周): 
  - 完成数据库设置
  - 配置AnythingLLM
  - 调整后端API

- **阶段2** (2-3周):
  - 实现用户反馈功能
  - 开发聊天历史功能
  - 编写测试

- **阶段3** (1-2周):
  - 进行性能优化
  - 准备部署方案
  - 用户测试和调整

## 7. 问题和风险

1. **知识库质量**: 心理健康知识文档的质量和覆盖面将直接影响RAG效果
2. **模型选择**: 需要选择适合中文心理健康领域的LLM和embedding模型
3. **资源消耗**: AnythingLLM会占用较多系统资源，需要适当配置服务器
4. **隐私安全**: 心理健康数据敏感，需加强数据保护措施

---

本计划将随项目进展不断更新。开发团队应定期检查此文档，确保开发方向与计划保持一致。