import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      // Proxy /api requests to your FastAPI backend
      '/api': {
        target: 'http://127.0.0.1:8000', // Your backend address
        changeOrigin: true,
      }
    }
  }
})
