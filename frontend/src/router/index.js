import ChatView from '../views/ChatView.vue'
import ResourcePage from '../views/ResourcePage.vue'

const routes = [
  {
    path: '/',
    redirect: '/chat'
  },
  {
    path: '/chat',
    name: 'chat',
    component: ChatView,
    meta: {
      title: 'Mental Health Chat'
    }
  },
  {
    path: '/resources',
    name: 'resources',
    component: ResourcePage,
    meta: {
      title: 'Mental Health Resources'
    }
  }
]

export default routes
