import { createApp } from 'vue' // 从vue库导入createApp函数，用于创建Vue应用实例
import { createRouter, createWebHistory } from 'vue-router' // 从vue-router库导入创建路由所需函数
import ElementPlus from 'element-plus' // 导入Element Plus UI库
import 'element-plus/dist/index.css' // 导入Element Plus的样式文件
import App from './App.vue' // 导入根组件App.vue
import routes from './router' // 导入路由配置

// Create Vue Router instance // 创建Vue Router实例
const router = createRouter({ // 调用createRouter创建路由器
  history: createWebHistory(), // 使用history模式，利用HTML5 History API
  routes // 传入路由配置
}) // 路由器创建结束

// Create and mount the Vue application // 创建并挂载Vue应用
const app = createApp(App) // 调用createApp，传入根组件App，创建应用实例

// Use plugins // 使用插件
app.use(ElementPlus) // 安装Element Plus插件
app.use(router) // 安装Vue Router插件

// Mount and signal that app is ready // 挂载应用并发送应用已准备好的信号
app.mount('#app') // 将应用实例挂载到id为'app'的DOM元素上
if (window.appMounted) { // 检查window对象上是否存在appMounted函数
  window.appMounted() // 如果存在，则调用该函数（用于IDE或其他环境的挂载信号）
} // if结束
