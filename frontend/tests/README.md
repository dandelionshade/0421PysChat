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
npm install --save-dev vitest @vue/test-utils jsdom

# 运行测试
npm test

# 运行测试并监视文件变更
npm run test:watch

# 运行测试并生成覆盖率报告
npm run test:coverage
```

## 为前端添加测试

1. 在`package.json`中添加测试脚本：
```json
"scripts": {
  "test": "vitest run",
  "test:watch": "vitest",
  "test:coverage": "vitest run --coverage"
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

## 测试最佳实践

1. **测试组件渲染**：确保组件能正确渲染UI元素
   ```javascript
   it('renders the chat interface', () => {
     const wrapper = mount(ChatView);
     expect(wrapper.find('.chat-container').exists()).toBe(true);
   });
   ```

2. **测试用户交互**：模拟用户输入和点击
   ```javascript
   it('sends a message when button is clicked', async () => {
     const wrapper = mount(ChatView);
     await wrapper.setData({ userInput: 'Hello' });
     await wrapper.find('.send-button').trigger('click');
     // 验证结果...
   });
   ```

3. **测试API调用**：模拟API服务和响应
   ```javascript
   it('calls the API when sending a message', async () => {
     // 设置API模拟
     const mockApi = { sendMessage: vi.fn().mockResolvedValue({...}) };
     // 挂载组件并传入模拟的API
     const wrapper = mount(ChatView, {
       global: { provide: { api: mockApi } }
     });
     // 测试交互及验证API调用
   });
   ```

4. **测试错误处理**：确保组件能处理错误情况
   ```javascript
   it('handles API errors gracefully', async () => {
     const mockApi = { sendMessage: vi.fn().mockRejectedValue(new Error('API Error')) };
     // 测试组件的错误处理...
   });
   ```

5. **快照测试**：验证UI没有意外变化
   ```javascript
   it('matches snapshot', () => {
     const wrapper = mount(ChatView);
     expect(wrapper.html()).toMatchSnapshot();
   });
   ```
