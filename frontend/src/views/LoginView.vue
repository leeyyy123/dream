<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login, signUp } from '../services/api'
import {
  DocumentAdd,
  DataAnalysis,
  TrendCharts,
  Moon,
  User,
  Lock
} from '@element-plus/icons-vue'

const router = useRouter()

// 登录表单数据
const loginForm = ref({
  email: '',
  password: ''
})

// 注册表单数据
const registerForm = ref({
  name: '',
  email: '',
  password: '',
  confirmPassword: ''
})

// 当前活动标签
const activeTab = ref('login')

// 登录函数
const handleLogin = async () => {
  try {
    const response = await login(loginForm.value.email, loginForm.value.password)
    console.log('登录响应:', response)

    if (response.Code === 200 || response.Code === 202) {
      if (response.Token) {
        localStorage.setItem('authToken', response.Token)
        localStorage.setItem('userId', response.UserID)
        if (response.Code === 202) {
          localStorage.setItem('isAdmin', 'true')
        } else {
          localStorage.setItem('isAdmin', 'false')
        }
      }
      router.push('/main/home')
    } else {
      alert(`登录失败: ${response.Msg}`)
    }
  } catch (error) {
    console.error('登录错误:', error)
    alert('登录过程中发生错误')
  }
}

// 注册函数
const register = async () => {
  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    alert('密码和确认密码不匹配')
    return
  }

  try {
    const response = await signUp(
      registerForm.value.name,
      registerForm.value.email,
      registerForm.value.password
    )
    console.log('注册响应:', response)

    if (response.Code === 200) {
      alert('注册成功！请登录')
      activeTab.value = 'login'
    } else {
      alert(`注册失败: ${response.Msg}`)
    }
  } catch (error) {
    console.error('注册错误:', error)
    alert('注册过程中发生错误')
  }
}
</script>

<template>
  <div class="login-container">
    <!-- 左侧品牌区域 -->
    <div class="brand-section">
      <div class="brand-content">
        <div class="logo-wrapper">
          <component :is="Moon" class="logo-icon" />
        </div>
        <h1 class="brand-title">Dream</h1>
        <p class="brand-subtitle">专业梦境记录与分析平台</p>
        <div class="features">
          <div class="feature-item">
            <div class="feature-icon">
              <component :is="DocumentAdd" />
            </div>
            <span>智能记录梦境</span>
          </div>
          <div class="feature-item">
            <div class="feature-icon">
              <component :is="DataAnalysis" />
            </div>
            <span>深度心理分析</span>
          </div>
          <div class="feature-item">
            <div class="feature-icon">
              <component :is="TrendCharts" />
            </div>
            <span>可视化数据报告</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧登录区域 -->
    <div class="login-section">
      <div class="login-card">
        <!-- 标签切换 -->
        <div class="tab-switch">
          <button
            :class="['tab-button', { active: activeTab === 'login' }]"
            @click="activeTab = 'login'"
          >
            登录
          </button>
          <button
            :class="['tab-button', { active: activeTab === 'register' }]"
            @click="activeTab = 'register'"
          >
            注册
          </button>
        </div>

        <!-- 登录表单 -->
        <form v-if="activeTab === 'login'" @submit.prevent="handleLogin" class="form">
          <div class="form-group">
            <label for="login-email" class="form-label">邮箱地址</label>
            <div class="input-with-icon">
              <component :is="User" class="input-icon" />
              <input
                id="login-email"
                v-model="loginForm.email"
                type="email"
                required
                placeholder="请输入邮箱地址"
                class="spa-input"
              />
            </div>
          </div>

          <div class="form-group">
            <label for="login-password" class="form-label">密码</label>
            <div class="input-with-icon">
              <component :is="Lock" class="input-icon" />
              <input
                id="login-password"
                v-model="loginForm.password"
                type="password"
                required
                placeholder="请输入密码"
                class="spa-input"
              />
            </div>
          </div>

          <button type="submit" class="spa-button-primary submit-button">
            登录账户
          </button>
        </form>

        <!-- 注册表单 -->
        <form v-else-if="activeTab === 'register'" @submit.prevent="register" class="form">
          <div class="form-group">
            <label for="register-name" class="form-label">用户名</label>
            <div class="input-with-icon">
              <component :is="User" class="input-icon" />
              <input
                id="register-name"
                v-model="registerForm.name"
                type="text"
                required
                placeholder="请输入用户名"
                class="spa-input"
              />
            </div>
          </div>

          <div class="form-group">
            <label for="register-email" class="form-label">邮箱地址</label>
            <div class="input-with-icon">
              <component :is="User" class="input-icon" />
              <input
                id="register-email"
                v-model="registerForm.email"
                type="email"
                required
                placeholder="请输入邮箱地址"
                class="spa-input"
              />
            </div>
          </div>

          <div class="form-group">
            <label for="register-password" class="form-label">密码</label>
            <div class="input-with-icon">
              <component :is="Lock" class="input-icon" />
              <input
                id="register-password"
                v-model="registerForm.password"
                type="password"
                required
                placeholder="请输入密码"
                class="spa-input"
              />
            </div>
          </div>

          <div class="form-group">
            <label for="confirm-password" class="form-label">确认密码</label>
            <div class="input-with-icon">
              <component :is="Lock" class="input-icon" />
              <input
                id="confirm-password"
                v-model="registerForm.confirmPassword"
                type="password"
                required
                placeholder="请再次输入密码"
                class="spa-input"
              />
            </div>
          </div>

          <button type="submit" class="spa-button-primary submit-button">
            创建账户
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  min-height: 100vh;
  background: var(--neutral-50);
  display: flex;
  position: relative;
}

/* 左侧品牌区域 */
.brand-section {
  flex: 1;
  background: var(--neutral-900);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-10);
  position: relative;
  overflow: hidden;
}

.brand-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E") repeat;
  opacity: 0.1;
}

.brand-content {
  text-align: center;
  color: white;
  position: relative;
  z-index: 1;
  max-width: 400px;
}

.logo-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 96px;
  height: 96px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-2xl);
  margin-bottom: var(--space-6);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
}

.logo-icon {
  width: 48px;
  height: 48px;
}

.brand-title {
  font-size: var(--text-4xl);
  font-weight: var(--font-bold);
  margin: 0 0 var(--space-4) 0;
  letter-spacing: var(--tracking-tight);
}

.brand-subtitle {
  font-size: var(--text-lg);
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 var(--space-12) 0;
  font-weight: var(--font-regular);
}

.features {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.feature-item {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  font-size: var(--text-base);
  color: rgba(255, 255, 255, 0.9);
}

.feature-icon {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
}

.feature-icon > * {
  width: 20px;
  height: 20px;
}

/* 右侧登录区域 */
.login-section {
  flex: 0 0 480px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-6);
  background: white;
}

.login-card {
  width: 100%;
  max-width: 400px;
}

/* 标签切换 */
.tab-switch {
  display: flex;
  background: var(--neutral-100);
  border-radius: var(--radius-lg);
  padding: 4px;
  margin-bottom: var(--space-10);
  border: 1px solid var(--border-color);
}

.tab-button {
  flex: 1;
  padding: var(--space-3) var(--space-4);
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--neutral-600);
  cursor: pointer;
  transition: var(--transition-base);
}

.tab-button.active {
  background: white;
  color: var(--neutral-900);
  box-shadow: var(--shadow-sm);
}

.tab-button:hover:not(.active) {
  color: var(--neutral-700);
}

/* 表单样式 */
.form {
  text-align: left;
}

.form-group {
  margin-bottom: var(--space-6);
}

.form-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--neutral-700);
  margin-bottom: var(--space-2);
}

.input-with-icon {
  position: relative;
}

.input-icon {
  position: absolute;
  left: var(--space-3);
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  color: var(--neutral-400);
}

.input-with-icon .spa-input {
  padding-left: var(--space-10);
}

.spa-input {
  width: 100%;
  padding: var(--space-2_5) var(--space-3);
  background: white;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  font-size: var(--text-base);
  color: var(--neutral-900);
  transition: all var(--transition-fast);
}

.spa-input:focus {
  outline: none;
  border-color: var(--border-color-focus);
  box-shadow: 0 0 0 3px rgb(100 116 139 / 0.1);
}

.spa-input::placeholder {
  color: var(--neutral-400);
}

.submit-button {
  width: 100%;
  padding: var(--space-4);
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  margin-top: var(--space-8);
  display: flex;
  align-items: center;
  justify-content: center;
}

.spa-button-primary {
  background: var(--neutral-900);
  color: white;
  border: none;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-base);
}

.spa-button-primary:hover {
  background: var(--neutral-800);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .brand-section {
    flex: 0 0 40%;
  }

  .login-section {
    flex: 0 0 60%;
  }
}

@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
  }

  .brand-section {
    flex: 0 0 auto;
    min-height: 300px;
    padding: var(--space-8);
  }

  .brand-title {
    font-size: var(--text-3xl);
  }

  .login-section {
    flex: 1;
    padding: var(--space-4);
  }

  .features {
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: center;
    gap: var(--space-4);
  }

  .feature-item {
    font-size: var(--text-sm);
  }

  .feature-icon {
    width: 36px;
    height: 36px;
  }

  .feature-icon > * {
    width: 18px;
    height: 18px;
  }
}

@media (max-width: 480px) {
  .login-section {
    padding: var(--space-4) var(--space-2);
  }

  .brand-content {
    padding: 0 var(--space-2);
  }

  .logo-wrapper {
    width: 80px;
    height: 80px;
    margin-bottom: var(--space-4);
  }

  .logo-icon {
    width: 40px;
    height: 40px;
  }

  .brand-title {
    font-size: var(--text-2xl);
  }

  .brand-subtitle {
    font-size: var(--text-base);
    margin-bottom: var(--space-8);
  }
}
</style>
