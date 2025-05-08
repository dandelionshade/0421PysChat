# 前端测试

## 目录结构
- `unit/`: 单元测试文件
  - `ChatView.spec.js`: 聊天视图组件测试
  - `ResourcePage.spec.js`: 资源页面组件测试

## 运行测试
```bash
# 进入frontend目录
cd frontend

# 安装开发依赖（如果尚未安装）
npm install --save-dev vitest @vue/test-utils

# 运行测试
npm test
```

## 为前端添加测试

1. 在`package.json`中添加测试脚本：
```json
"scripts": {
  "test": "vitest run",
  "test:watch": "vitest"
}
```

2. 创建测试文件：在`tests/unit`目录下创建以`.spec.js`结尾的测试文件

3. 编写测试：使用Vitest和Vue Test Utils编写组件测试

## 测试覆盖率

运行带覆盖率报告的测试：
```bash
npm run test:coverage
```

覆盖率报告将显示在终端中，并在`coverage`目录中生成详细报告。
