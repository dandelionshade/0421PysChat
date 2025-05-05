import axios from 'axios'; // 导入axios库，用于发送HTTP请求

// Create axios instance with default config // 创建一个配置了默认值的axios实例
const api = axios.create({ // 调用axios.create方法创建一个新的axios实例
  baseURL: '/api', // This works with our Vite proxy configuration // 设置API的基础URL为'/api'，这会与Vite的代理配置协同工作
  headers: { // 配置请求头
    'Content-Type': 'application/json', // 设置Content-Type为application/json
  }, // headers配置结束
  timeout: 30000, // 30 second timeout (LLM responses can be slow) // 设置请求超时时间为30000毫秒（30秒），考虑到LLM响应可能较慢
}); // axios实例创建结束

export default { // 导出包含API方法的对象
  // Chat API // 聊天相关的API
  sendMessage(message) { // 定义sendMessage方法，用于发送聊天消息
    return api.post('/chat', { message }); // 使用创建的api实例发送POST请求到'/chat'，请求体包含message
  }, // sendMessage方法结束
  
  // Resources API // 资源相关的API
  getResources(params = {}) { // 定义getResources方法，用于获取资源列表，可接受可选的params参数
    return api.get('/resources', { params }); // 使用创建的api实例发送GET请求到'/resources'，并将params作为查询参数
  } // getResources方法结束
}; // 导出对象结束
