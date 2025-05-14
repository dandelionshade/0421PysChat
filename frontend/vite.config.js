import { defineConfig } from 'vite' // 从vite导入defineConfig函数，用于定义Vite配置
import vue from '@vitejs/plugin-vue' // 导入Vite的Vue插件

// https://vitejs.dev/config/ // Vite配置文档链接
export default defineConfig({ // 导出Vite配置对象
  plugins: [vue()], // 使用Vue插件
  server: { // 开发服务器配置
    proxy: { // 配置代理
      // Proxy /api requests to your FastAPI backend // 将/api请求代理到你的FastAPI后端
      '/api': { // 匹配/api开头的请求路径
        target: 'http://127.0.0.1:8000', // Your backend address // 目标地址是FastAPI后端运行的地址
        changeOrigin: true, // 改变请求的源，使其与目标地址一致
      }, // 代理配置结束
      // Optional: Direct proxy for AnythingLLM API
      '/v1': {
        target: 'http://localhost:3001',
        changeOrigin: true,
      }
    } // proxy配置结束
  } // server配置结束
}) // defineConfig结束
