import ChatView from '../views/ChatView.vue' // 导入ChatView组件
import ResourcePage from '../views/ResourcePage.vue' // 导入ResourcePage组件

const routes = [ // 定义路由配置数组
  { // 第一个路由对象
    path: '/', // 路径为根路径
    redirect: '/chat' // 重定向到/chat路径
  }, // 路由对象结束
  { // 第二个路由对象
    path: '/chat', // 路径为/chat
    name: 'chat', // 路由名称为chat
    component: ChatView, // 对应的组件是ChatView
    meta: { // 路由元信息
      title: 'Mental Health Chat' // 页面标题
    } // meta结束
  }, // 路由对象结束
  { // 第三个路由对象
    path: '/resources', // 路径为/resources
    name: 'resources', // 路由名称为resources
    component: ResourcePage, // 对应的组件是ResourcePage
    meta: { // 路由元信息
      title: 'Mental Health Resources' // 页面标题
    } // meta结束
  } // 路由对象结束
] // 路由数组结束

export default routes // 导出路由配置数组
