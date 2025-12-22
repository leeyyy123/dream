<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getUserInfo } from '../services/api'

const router = useRouter()
const route = useRoute()

// 导航菜单项
const navItems = ref([
  { name: '首页', path: '/main/home', emoji: '🏠' },
  { name: '记录梦境', path: '/create-dream', emoji: '🌙' },
  { name: '分析梦境', path: '/main/dream-analysis', emoji: '🧠' },
  { name: '我的梦境', path: '/main/my-dreams', emoji: '📖' }
])

const activeItem = ref('首页')

// 用户信息和头像状态
const showUserMenu = ref(false)
const userInfo = ref({
  username: '用户名',
  email: 'user@example.com',
  avatar: null
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

onMounted(async () => {
  const currentPath = route.path
  const currentItem = navItems.value.find(item => item.path === currentPath)
  if (currentItem) {
    activeItem.value = currentItem.name
  }

  await fetchUserInfo()
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
              <span class="brand-emoji">🌙</span>
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
                <span class="nav-emoji">{{ item.emoji }}</span>
                <span class="nav-text">{{ item.name }}</span>
              </div>
            </div>

            <!-- 用户菜单 -->
            <div class="user-menu-container">
              <div class="user-avatar" @click="toggleUserMenu">
                <img
                  v-if="userInfo.avatar"
                  :src="userInfo.avatar"
                  :alt="userInfo.username"
                  class="avatar-img"
                />
                <div v-else class="default-avatar">
                  <span class="user-emoji">👤</span>
                </div>
              </div>

              <!-- 用户下拉菜单 -->
              <div v-if="showUserMenu" class="user-dropdown">
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
            <h1 class="welcome-title">欢迎回来，{{ userInfo.username }}！</h1>
            <p class="welcome-description">
              开始记录和分析你的梦境，探索潜意识的奥秘。
            </p>
            <div class="quick-actions">
              <router-link to="/create-dream" class="spa-button-primary action-button">
                <span class="action-icon">✨</span>
                <span>记录新梦境</span>
              </router-link>
              <router-link to="/main/dream-analysis" class="spa-button-secondary action-button">
                <span class="action-icon">🧠</span>
                <span>开始分析</span>
              </router-link>
            </div>
          </div>
        </div>

        <!-- 统计卡片 -->
        <div class="stats-grid">
          <div class="stat-card spa-card">
            <div class="stat-icon">
              <span>📖</span>
            </div>
            <div class="stat-content">
              <div class="stat-value">0</div>
              <div class="stat-label">梦境总数</div>
            </div>
          </div>

          <div class="stat-card spa-card">
            <div class="stat-icon">
              <span>📊</span>
            </div>
            <div class="stat-content">
              <div class="stat-value">0</div>
              <div class="stat-label">分析报告</div>
            </div>
          </div>

          <div class="stat-card spa-card">
            <div class="stat-icon">
              <span>📈</span>
            </div>
            <div class="stat-content">
              <div class="stat-value">0</div>
              <div class="stat-label">本月记录</div>
            </div>
          </div>
        </div>

        <!-- 快速操作 -->
        <div class="recent-dreams-section">
          <h2 class="section-title">最近梦境</h2>
          <div class="recent-dreams">
            <div class="empty-state">
              <div class="empty-icon">🌙</div>
              <h3 class="empty-title">还没有梦境记录</h3>
              <p class="empty-description">开始记录你的第一个梦境吧</p>
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
  z-index: 50;
  backdrop-filter: blur(12px);
  background: rgba(255, 255, 255, 0.95);
}

.nav-content {
  display: flex;
  align-items: center;
  height: 72px;
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
  width: 40px;
  height: 40px;
  background: var(--primary-700);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.brand-emoji {
  font-size: 20px;
  color: white;
}

.brand-text {
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--neutral-900);
  letter-spacing: -0.5px;
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
  gap: var(--space-2);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: var(--transition-base);
  color: var(--neutral-600);
  font-size: var(--text-sm);
  font-weight: 500;
  position: relative;
}

.nav-item:hover {
  background: var(--neutral-100);
  color: var(--neutral-900);
}

.nav-item.active {
  background: var(--primary-50);
  color: var(--primary-700);
  font-weight: 600;
}

.nav-emoji {
  font-size: 16px;
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
  width: 40px;
  height: 40px;
  border-radius: var(--radius-full);
  cursor: pointer;
  overflow: hidden;
  border: 2px solid var(--border-color);
  transition: var(--transition-base);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--neutral-100);
}

.user-avatar:hover {
  border-color: var(--primary-300);
  box-shadow: var(--shadow-md);
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
}

.user-emoji {
  font-size: 20px;
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
  z-index: 100;
  overflow: hidden;
  animation: slideDown var(--transition-base) ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.user-info {
  padding: var(--space-4);
  border-bottom: 1px solid var(--border-color);
}

.user-name {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--neutral-900);
  margin-bottom: var(--space-1);
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
  padding: var(--space-3) var(--space-4);
  background: transparent;
  border: none;
  text-align: left;
  font-size: var(--text-sm);
  color: var(--neutral-700);
  cursor: pointer;
  transition: var(--transition-base);
  display: flex;
  align-items: center;
  gap: var(--space-3);
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
  min-height: calc(100vh - 72px);
}

/* 欢迎区域 */
.welcome-section {
  text-align: center;
  padding: var(--space-16) 0;
}

.welcome-content {
  max-width: 600px;
  margin: 0 auto;
}

.welcome-title {
  font-size: var(--text-4xl);
  font-weight: 700;
  color: var(--neutral-900);
  margin: 0 0 var(--space-4) 0;
  line-height: 1.2;
}

.welcome-description {
  font-size: var(--text-lg);
  color: var(--neutral-600);
  margin: 0 0 var(--space-8) 0;
  line-height: 1.6;
}

.quick-actions {
  display: flex;
  gap: var(--space-4);
  justify-content: center;
  flex-wrap: wrap;
}

.action-button {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-4) var(--space-6);
}

.action-icon {
  font-size: 18px;
}

/* 统计网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-6);
  margin: var(--space-16) 0;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-6);
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--primary-500), var(--primary-600));
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: var(--primary-50);
  color: var(--primary-600);
  border-radius: var(--radius-xl);
  font-size: 24px;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: var(--text-2xl);
  font-weight: 700;
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
  margin-top: var(--space-16);
}

.section-title {
  font-size: var(--text-2xl);
  font-weight: 600;
  color: var(--neutral-900);
  margin: 0 0 var(--space-8) 0;
}

.recent-dreams {
  margin-top: var(--space-6);
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: var(--space-20) var(--space-4);
}

.empty-icon {
  font-size: 64px;
  color: var(--neutral-400);
  margin-bottom: var(--space-6);
}

.empty-title {
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--neutral-700);
  margin: 0 0 var(--space-2) 0;
}

.empty-description {
  font-size: var(--text-base);
  color: var(--neutral-600);
  margin: 0 0 var(--space-6) 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-content {
    padding: 0 var(--space-4);
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
    gap: var(--space-4);
  }
}

@media (max-width: 480px) {
  .welcome-title {
    font-size: var(--text-3xl);
  }

  .stats-grid {
    grid-template-columns: 1fr;
    gap: var(--space-4);
  }
}
</style>