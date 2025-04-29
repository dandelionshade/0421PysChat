import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import routes from './router'

// Create Vue Router instance
const router = createRouter({
  history: createWebHistory(),
  routes
})

// Create and mount the Vue application
const app = createApp(App)

// Use plugins
app.use(ElementPlus)
app.use(router)

// Mount and signal that app is ready
app.mount('#app')
if (window.appMounted) {
  window.appMounted()
}
