<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getUserInfo, getUserStatistics } from '../services/api'
import {
  House,
  DataAnalysis,
  Reading,
  User,
  DocumentAdd,
  TrendCharts,
  DataLine,
  Close,
  Moon
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

// API 基础URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8888'

// 导航菜单项
const navItems = ref([
  { name: '首页', path: '/main/home', icon: House },
  { name: '记录梦境', path: '/create-dream', icon: DocumentAdd },
  { name: '分析梦境', path: '/main/dream-analysis', icon: DataAnalysis },
  { name: '我的梦境', path: '/main/my-dreams', icon: Reading }
])

const activeItem = ref('首页')

// 用户信息和头像状态
const showUserMenu = ref(false)
const userInfo = ref({
  username: '用户名',
  email: 'user@example.com',
  avatar: null
})

// 统计数据
const statistics = ref({
  totalDreams: 0,
  totalAnalyses: 0,
  monthlyDreams: 0,
  recentDreams: []
})

// 计算完整的头像URL
const fullAvatarUrl = computed(() => {
  if (!userInfo.value.avatar) return null
  // 如果已经是完整URL，直接返回
  if (userInfo.value.avatar.startsWith('http://') || userInfo.value.avatar.startsWith('https://')) {
    return userInfo.value.avatar
  }
  // 拼接API基础URL
  return `${API_BASE_URL}${userInfo.value.avatar}`
})

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    const token = localStorage.getItem('authToken')
    if (!token) {
      userInfo.value = {
        username: '游客',
        email: 'guest@example.com',
        avatar: null
      }
      return
    }

    const response = await getUserInfo(token)

    if (response.Code === 200 && response.Data) {
      userInfo.value = {
        username: response.Data.UserName || '用户',
        email: response.Data.Email || 'user@example.com',
        avatar: response.Data.AvatarUrl || null
      }

      localStorage.setItem('username', userInfo.value.username)
      localStorage.setItem('userEmail', userInfo.value.email)
    } else {
      const storedUsername = localStorage.getItem('username') || '用户'
      const storedEmail = localStorage.getItem('userEmail') || 'user@example.com'

      userInfo.value = {
        username: storedUsername,
        email: storedEmail,
        avatar: null
      }
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
    const storedUsername = localStorage.getItem('username') || '用户'
    const storedEmail = localStorage.getItem('userEmail') || 'user@example.com'

    userInfo.value = {
      username: storedUsername,
      email: storedEmail,
      avatar: null
    }
  }
}

// 获取统计数据
const fetchStatistics = async () => {
  try {
    const token = localStorage.getItem('authToken')
    if (!token) {
      statistics.value = {
        totalDreams: 0,
        totalAnalyses: 0,
        monthlyDreams: 0,
        recentDreams: []
      }
      return
    }

    const response = await getUserStatistics(token)

    if (response.Code === 200 && response.Data) {
      statistics.value = {
        totalDreams: response.Data.totalDreams || 0,
        totalAnalyses: response.Data.totalAnalyses || 0,
        monthlyDreams: response.Data.monthlyDreams || 0,
        recentDreams: response.Data.recentDreams || []
      }
    } else {
      console.error('获取统计数据失败:', response.Msg)
    }
  } catch (error) {
    console.error('获取统计数据异常:', error)
  }
}

// 处理导航点击
const handleNavClick = (item) => {
  activeItem.value = item.name
  router.push(item.path)
}

// 退出登录
const logout = () => {
  localStorage.removeItem('authToken')
  localStorage.removeItem('userId')
  localStorage.removeItem('isAdmin')
  localStorage.removeItem('username')
  localStorage.removeItem('userEmail')
  showUserMenu.value = false
  router.push('/')
}

// 切换用户菜单
const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

// 查看个人信息
const viewProfile = () => {
  showUserMenu.value = false
  router.push('/main/profile')
}

// 点击外部关闭菜单
const handleClickOutside = (event) => {
  const userMenuEl = document.querySelector('.user-menu-container')
  if (userMenuEl && !userMenuEl.contains(event.target)) {
    showUserMenu.value = false
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

onMounted(async () => {
  const currentPath = route.path
  const currentItem = navItems.value.find(item => item.path === currentPath)
  if (currentItem) {
    activeItem.value = currentItem.name
  }

  await fetchUserInfo()
  await fetchStatistics()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div class="home-layout">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="spa-container">
        <div class="nav-content">
          <!-- 品牌区域 -->
          <div class="nav-brand">
            <div class="brand-logo">
              <component :is="Moon" class="brand-icon" />
            </div>
            <span class="brand-text">Dream</span>
          </div>

          <!-- 右侧区域：导航菜单 + 用户菜单 -->
          <div class="nav-right">
            <!-- 导航菜单 -->
            <div class="nav-menu">
              <div
                v-for="item in navItems"
                :key="item.path"
                :class="['nav-item', { active: activeItem === item.name }]"
                @click="handleNavClick(item)"
              >
                <component :is="item.icon" class="nav-icon" />
                <span class="nav-text">{{ item.name }}</span>
              </div>
            </div>

            <!-- 用户菜单 -->
            <div class="user-menu-container">
              <div class="user-avatar" @click="toggleUserMenu">
                <img
                  v-if="fullAvatarUrl"
                  :src="fullAvatarUrl"
                  :alt="userInfo.username"
                  class="avatar-img"
                />
                <div v-else class="default-avatar">
                  <component :is="User" class="user-icon" />
                </div>
              </div>

              <!-- 用户下拉菜单 -->
              <div v-if="showUserMenu" class="user-dropdown animate-slide-down">
                <div class="user-info">
                  <div class="user-name">{{ userInfo.username }}</div>
                  <div class="user-email">{{ userInfo.email }}</div>
                </div>
                <div class="dropdown-divider"></div>
                <button class="dropdown-item" @click="viewProfile">
                  个人信息
                </button>
                <button class="dropdown-item dropdown-item-danger" @click="logout">
                  退出登录
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主内容区域 -->
    <main class="main-content">
      <div class="spa-container">
        <div class="welcome-section">
          <div class="welcome-content">
            <h1 class="welcome-title">欢迎回来，{{ userInfo.username }}</h1>
            <p class="welcome-description">
              记录梦境，探索内心世界
            </p>
            <div class="quick-actions">
              <router-link to="/create-dream" class="action-button spa-button-primary">
                <component :is="DocumentAdd" class="action-icon" />
                <span>记录新梦境</span>
              </router-link>
              <router-link to="/main/dream-analysis" class="action-button spa-button-secondary">
                <component :is="DataAnalysis" class="action-icon" />
                <span>开始分析</span>
              </router-link>
            </div>
          </div>
        </div>

        <!-- 统计卡片 -->
        <div class="stats-grid">
          <div class="stat-card spa-card">
            <div class="stat-icon">
              <component :is="Reading" />
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ statistics.totalDreams }}</div>
              <div class="stat-label">梦境总数</div>
            </div>
          </div>

          <div class="stat-card spa-card">
            <div class="stat-icon">
              <component :is="DataAnalysis" />
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ statistics.totalAnalyses }}</div>
              <div class="stat-label">分析报告</div>
            </div>
          </div>

          <div class="stat-card spa-card">
            <div class="stat-icon">
              <component :is="DataLine" />
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ statistics.monthlyDreams }}</div>
              <div class="stat-label">本月记录</div>
            </div>
          </div>
        </div>

        <!-- 快速操作 -->
        <div class="recent-dreams-section">
          <h2 class="section-title">最近梦境</h2>
          <div class="recent-dreams">
            <div v-if="statistics.recentDreams && statistics.recentDreams.length > 0" class="recent-dreams-list">
              <div
                v-for="dream in statistics.recentDreams"
                :key="dream.DreamID"
                class="recent-dream-card spa-card"
              >
                <div class="dream-header">
                  <h3 class="dream-title">{{ dream.Title }}</h3>
                  <span class="dream-date">{{ formatDate(dream.DreamDate) }}</span>
                </div>
                <p class="dream-preview">{{ dream.ContentPreview }}...</p>
                <router-link :to="`/main/my-dreams`" class="view-more-link">
                  查看详情 →
                </router-link>
              </div>
            </div>
            <div v-else class="empty-state">
              <div class="empty-icon">
                <component :is="Moon" />
              </div>
              <h3 class="empty-title">还没有梦境记录</h3>
              <p class="empty-description">开始记录你的第一个梦境</p>
              <router-link to="/create-dream" class="spa-button-primary">
                记录梦境
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.home-layout {
  min-height: 100vh;
  background: var(--neutral-50);
}

/* 导航栏 */
.navbar {
  background: white;
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
  backdrop-filter: blur(12px);
  background: rgba(255, 255, 255, 0.95);
}

.nav-content {
  display: flex;
  align-items: center;
  height: 68px;
  justify-content: space-between;
}

/* 品牌区域 */
.nav-brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-shrink: 0;
}

.brand-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  background: var(--neutral-900);
  border-radius: var(--radius-lg);
  color: white;
}

.brand-icon {
  width: 20px;
  height: 20px;
}

.brand-text {
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  color: var(--neutral-900);
  letter-spacing: var(--tracking-tight);
}

/* 右侧区域 */
.nav-right {
  display: flex;
  align-items: center;
  gap: var(--space-8);
}

/* 导航菜单 */
.nav-menu {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
  color: var(--neutral-600);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
}

.nav-item:hover {
  background: var(--neutral-100);
  color: var(--neutral-900);
}

.nav-item.active {
  background: var(--neutral-100);
  color: var(--neutral-900);
  font-weight: var(--font-semibold);
}

.nav-icon {
  width: 18px;
  height: 18px;
}

.nav-text {
  white-space: nowrap;
}

/* 用户菜单 */
.user-menu-container {
  position: relative;
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.user-avatar {
  width: 38px;
  height: 38px;
  border-radius: var(--radius-full);
  cursor: pointer;
  overflow: hidden;
  border: 1px solid var(--border-color);
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--neutral-100);
}

.user-avatar:hover {
  border-color: var(--neutral-300);
  box-shadow: var(--shadow-sm);
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.default-avatar {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--neutral-500);
}

.user-icon {
  width: 20px;
  height: 20px;
}

/* 用户下拉菜单 */
.user-dropdown {
  position: absolute;
  top: calc(100% + var(--space-2));
  right: 0;
  min-width: 200px;
  background: white;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  border: 1px solid var(--border-color);
  z-index: var(--z-dropdown);
  overflow: hidden;
}

.user-info {
  padding: var(--space-4);
  border-bottom: 1px solid var(--border-color);
}

.user-name {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--neutral-900);
  margin-bottom: var(--space-0_5);
}

.user-email {
  font-size: var(--text-sm);
  color: var(--neutral-600);
}

.dropdown-divider {
  height: 1px;
  background: var(--border-color);
}

.dropdown-item {
  width: 100%;
  padding: var(--space-2_5) var(--space-4);
  background: transparent;
  border: none;
  text-align: left;
  font-size: var(--text-sm);
  color: var(--neutral-700);
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
}

.dropdown-item:hover {
  background: var(--neutral-50);
  color: var(--neutral-900);
}

.dropdown-item-danger:hover {
  background: var(--error-50);
  color: var(--error-600);
}

/* 主内容区域 */
.main-content {
  min-height: calc(100vh - 68px);
}

/* 欢迎区域 */
.welcome-section {
  text-align: center;
  padding: var(--space-16) 0 var(--space-12);
}

.welcome-content {
  max-width: 560px;
  margin: 0 auto;
}

.welcome-title {
  font-size: var(--text-4xl);
  font-weight: var(--font-bold);
  color: var(--neutral-900);
  margin: 0 0 var(--space-4) 0;
  line-height: var(--leading-tight);
  letter-spacing: var(--tracking-tight);
}

.welcome-description {
  font-size: var(--text-lg);
  color: var(--neutral-600);
  margin: 0 0 var(--space-8) 0;
  line-height: var(--leading-relaxed);
}

.quick-actions {
  display: flex;
  gap: var(--space-3);
  justify-content: center;
  flex-wrap: wrap;
}

.action-button {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-5);
}

.action-icon {
  width: 18px;
  height: 18px;
}

/* 统计网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: var(--space-5);
  margin: var(--space-12) 0;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-5);
  border: 1px solid var(--border-color);
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: var(--neutral-100);
  color: var(--neutral-700);
  border-radius: var(--radius-lg);
  flex-shrink: 0;
}

.stat-icon > * {
  width: 22px;
  height: 22px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--neutral-900);
  line-height: 1;
}

.stat-label {
  font-size: var(--text-sm);
  color: var(--neutral-600);
  margin-top: var(--space-1);
}

/* 最近梦境部分 */
.recent-dreams-section {
  margin-top: var(--space-12);
}

.section-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  color: var(--neutral-900);
  margin: 0 0 var(--space-6) 0;
}

.recent-dreams {
  margin-top: var(--space-5);
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: var(--space-16) var(--space-4);
}

.empty-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  background: var(--neutral-100);
  border-radius: var(--radius-xl);
  color: var(--neutral-400);
  margin: 0 auto var(--space-5);
}

.empty-icon > * {
  width: 28px;
  height: 28px;
}

.empty-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--neutral-800);
  margin: 0 0 var(--space-2) 0;
}

.empty-description {
  font-size: var(--text-base);
  color: var(--neutral-600);
  margin: 0 0 var(--space-5) 0;
}

/* 最近梦境列表 */
.recent-dreams-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--space-4);
}

.recent-dream-card {
  padding: var(--space-5);
  border: 1px solid var(--border-color);
}

.recent-dream-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.dream-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-3);
}

.dream-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--neutral-900);
  margin: 0;
  line-height: var(--leading-snug);
  flex: 1;
  margin-right: var(--space-3);
}

.dream-date {
  font-size: var(--text-sm);
  color: var(--neutral-500);
  white-space: nowrap;
}

.dream-preview {
  font-size: var(--text-sm);
  color: var(--neutral-600);
  line-height: var(--leading-relaxed);
  margin: 0 0 var(--space-4) 0;
}

.view-more-link {
  display: inline-flex;
  align-items: center;
  color: var(--neutral-900);
  text-decoration: none;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  transition: all var(--transition-fast);
}

.view-more-link:hover {
  color: var(--neutral-700);
  transform: translateX(2px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-content {
    height: 64px;
  }

  .nav-right {
    gap: var(--space-4);
  }

  .nav-menu {
    display: none;
  }

  .brand-text {
    font-size: var(--text-lg);
  }

  .main-content {
    min-height: calc(100vh - 64px);
  }

  .quick-actions {
    flex-direction: column;
    align-items: center;
  }

  .stats-grid {
    grid-template-columns: 1fr;
    gap: var(--space-3);
  }

  .welcome-section {
    padding: var(--space-10) 0 var(--space-8);
  }
}

@media (max-width: 480px) {
  .welcome-title {
    font-size: var(--text-3xl);
  }

  .stats-grid {
    grid-template-columns: 1fr;
    gap: var(--space-3);
  }
}
</style>
