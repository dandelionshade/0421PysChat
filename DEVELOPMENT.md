# PsyChat 开发文档

## 项目概述

PsyChat 是一个心理健康聊天应用，旨在提供用户与AI心理顾问进行交流的平台。本项目结合了现代Web开发技术和AI交互能力，为用户提供便捷的心理支持服务。

## 技术栈

### 前端

- **框架**: React.js
- **UI组件**: Material-UI / Ant Design
- **状态管理**: Redux / Context API
- **路由**: React Router
- **样式**: CSS/SCSS/Styled-Components
- **HTTP客户端**: Axios

### 后端

- **服务器**: Node.js / Express.js
- **数据库**: MongoDB / PostgreSQL
- **认证**: JWT
- **API**: RESTful / GraphQL

### AI集成

- **模型**: GPT或类似LLM模型
- **API**: OpenAI API / Azure OpenAI API

### 开发工具

- **包管理**: npm / yarn
- **构建工具**: Webpack / Vite
- **代码风格**: ESLint / Prettier
- **测试**: Jest / React Testing Library
- **版本控制**: Git

## 项目结构

```
e:\1_work\PersonalProgram\PsyChat\0421PsyChat\
├── client/                 # 前端代码
│   ├── public/             # 静态资源
│   ├── src/                # 源代码
│   │   ├── components/     # React组件
│   │   ├── pages/          # 页面组件
│   │   ├── services/       # API服务
│   │   ├── store/          # 状态管理
│   │   ├── styles/         # 样式文件
│   │   ├── utils/          # 工具函数
│   │   ├── App.js          # 主应用组件
│   │   └── index.js        # 入口文件
│   ├── package.json        # 依赖管理
│   └── README.md           # 前端说明文档
│
├── server/                 # 后端代码
│   ├── controllers/        # 请求控制器
│   ├── models/             # 数据模型
│   ├── routes/             # API路由
│   ├── services/           # 业务逻辑
│   ├── utils/              # 工具函数
│   ├── middleware/         # 中间件
│   ├── config/             # 配置文件
│   ├── app.js              # 应用入口
│   └── package.json        # 依赖管理
│
├── .gitignore              # Git忽略配置
├── DEVELOPMENT.md          # 开发文档(本文件)
├── CONTRIBUTING.md         # 贡献指南
└── README.md               # 项目总体说明
```

## 开发指南

### 环境设置

1. 安装Node.js (推荐v16+)和npm
2. 克隆项目仓库
3. 安装依赖:

   ```
   # 前端依赖
   cd client
   npm install
   
   # 后端依赖
   cd ../server
   npm install
   ```

### 开发流程

1. **前端开发**:

   ```
   cd client
   npm start
   ```

   前端开发服务器将在 <http://localhost:3000> 启动

2. **后端开发**:

   ```
   cd server
   npm run dev
   ```

   API服务器将在 <http://localhost:5000> 启动

### 代码规范

- 遵循ESLint配置的代码风格
- 组件使用功能组件和Hooks
- 使用异步/等待进行API调用
- 使用语义化命名

### 数据流

1. 用户在前端界面交互
2. React组件触发API请求
3. 后端接收请求并处理
4. 必要时与AI服务交互
5. 返回响应给前端
6. 前端更新状态并渲染UI

## API参考

### 用户认证

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/profile` - 获取用户资料

### 聊天功能

- `POST /api/chat/message` - 发送消息
- `GET /api/chat/history` - 获取聊天历史
- `GET /api/chat/sessions` - 获取所有会话

### AI交互

- `POST /api/ai/query` - 发送AI查询
- `GET /api/ai/suggestions` - 获取AI建议

## 部署流程

### 前端部署

1. 构建生产版本: `npm run build`
2. 将`build`目录部署到Web服务器或CDN

### 后端部署

1. 确保环境变量配置正确
2. 使用PM2或Docker进行部署
3. 设置数据库连接和备份策略

## 性能考量

- 实现消息缓存以减少API调用
- 使用懒加载和代码分割优化前端性能
- 实现请求限流防止API滥用
- 数据库索引优化

## 安全注意事项

- 所有API端点需进行适当的认证和授权
- 实现CSRF保护
- 敏感数据加密
- 确保AI交互符合隐私政策

```
