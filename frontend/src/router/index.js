import { createRouter, createWebHashHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import HomeView from '../views/HomeView.vue'
import CreateDreamView from '../views/CreateDreamView.vue'
import MyDreamsView from '../views/MyDreamsView.vue'
import DreamAnalysisView from '../views/DreamAnalysisView.vue'
import ProfileView from '../views/ProfileView.vue'
import AIChatView from '../views/AIChatView.vue'
import AdminLoginView from '../views/AdminLoginView.vue'
import AdminDashboardView from '../views/AdminDashboardView.vue'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: LoginView
  },
  {
    path: '/main/home',
    name: 'Main',
    component: HomeView
  },
  {
    path: '/main',
    redirect: '/main/home'
  },
  {
    path: '/create-dream',
    name: 'CreateDream',
    component: CreateDreamView
  },
  {
    path: '/main/my-dreams',
    name: 'MyDreams',
    component: MyDreamsView
  },
  {
    path: '/main/dream-analysis',
    name: 'DreamAnalysis',
    component: DreamAnalysisView
  },
  {
    path: '/main/profile',
    name: 'Profile',
    component: ProfileView
  },
  {
    path: '/edit-dream/:id',
    name: 'EditDream',
    component: CreateDreamView
  },
  {
    path: '/ai-chat',
    name: 'AIChat',
    component: AIChatView
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: AdminLoginView
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: AdminDashboardView
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router