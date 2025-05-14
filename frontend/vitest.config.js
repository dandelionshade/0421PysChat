import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  test: {
    // 启用类似jest的全局测试API
    globals: true,
    // 模拟DOM环境
    environment: 'jsdom',
    // 扩展匹配
    include: ['tests/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    // 排除node_modules和dist
    exclude: ['node_modules', 'dist', '../jsconfig.json'],
    // 配置测试覆盖率
    coverage: {
      reporter: ['text', 'html'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.{test,spec}.{js,ts}',
        'vitest.config.js',
        'vite.config.js',
      ],
    },
  },
})
