<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { adminLogin } from '../services/api'
import { Lock, User } from '@element-plus/icons-vue'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const error = ref('')
const loginForm = ref({
  email: '',
  password: ''
})

// 处理登录
const handleLogin = async () => {
  // 表单验证
  if (!loginForm.value.email.trim()) {
    error.value = '请输入管理员邮箱'
    return
  }

  if (!loginForm.value.password.trim()) {
    error.value = '请输入密码'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const response = await adminLogin(loginForm.value.email, loginForm.value.password)

    if (response.Code === 200) {
      // 保存token到localStorage
      localStorage.setItem('adminToken', response.Token)
      localStorage.setItem('adminEmail', response.Email)

      // 跳转到管理员主页面
      router.push('/admin/dashboard')
    } else {
      error.value = response.Msg || '登录失败'
    }
  } catch (err) {
    console.error('管理员登录失败:', err)
    error.value = '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 返回首页
const goBack = () => {
  router.push('/')
}
</script>

<template>
  <div class="admin-login-container">
    <!-- 头部 -->
    <header class="header">
      <div class="container">
        <div class="header-content">
          <button class="back-button" @click="goBack">
            <component :is="Lock" class="back-icon" />
            <span>返回</span>
          </button>
          <h1 class="page-title">管理员登录</h1>
          <div style="width: 80px;"></div>
        </div>
      </div>
    </header>

    <!-- 主要内容 -->
    <main class="main-content">
      <div class="container">
        <!-- 登录卡片 -->
        <div class="login-card spa-card">
          <div class="card-header">
            <div class="logo-section">
              <component :is="User" class="logo-icon" />
              <h2 class="logo-title">Dream 管理后台</h2>
            </div>
            <p class="logo-subtitle">请使用管理员账号登录</p>
          </div>

          <div class="card-content">
            <!-- 错误消息 -->
            <div v-if="error" class="alert alert-error">
              {{ error }}
            </div>

            <!-- 登录表单 -->
            <form class="login-form" @submit.prevent="handleLogin">
              <div class="form-group">
                <label class="form-label" for="email">管理员邮箱</label>
                <div class="input-wrapper">
                  <component :is="User" class="input-icon" />
                  <input
                    id="email"
                    v-model="loginForm.email"
                    type="email"
                    class="form-input spa-input"
                    placeholder="请输入管理员邮箱"
                    autocomplete="email"
                  />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label" for="password">密码</label>
                <div class="input-wrapper">
                  <component :is="Lock" class="input-icon" />
                  <input
                    id="password"
                    v-model="loginForm.password"
                    type="password"
                    class="form-input spa-input"
                    placeholder="请输入密码"
                    autocomplete="current-password"
                  />
                </div>
              </div>

              <button
                type="submit"
                class="login-button spa-button-primary"
                :disabled="loading"
              >
                {{ loading ? '登录中...' : '登录' }}
              </button>
            </form>

            <!-- 提示信息 -->
            <div class="tips-section">
              <p class="tip-text">默认管理员账号: admin@dream.com</p>
              <p class="tip-text">默认密码: 123456</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* 基础样式 */
.container {
  max-width: 500px;
  margin: 0 auto;
  padding: 0 var(--space-6);
}

/* 头部样式 */
.header {
  background: white;
  border-bottom: 1px solid var(--border-color);
  padding: var(--space-6) 0;
}

.header-content {
  display: flex;
  align-items: center;
  gap: var(--space-6);
}

.back-button {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2_5) var(--space-3);
  background: transparent;
  border: none;
  border-radius: var(--radius-lg);
  color: var(--neutral-700);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.back-button:hover {
  background: var(--neutral-100);
  color: var(--neutral-900);
}

.back-icon {
  width: 18px;
  height: 18px;
}

.page-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--neutral-900);
  margin: 0;
  flex: 1;
  letter-spacing: var(--tracking-tight);
}

/* 主内容区域 */
.main-content {
  padding: var(--space-12) 0;
  min-height: calc(100vh - 100px);
  display: flex;
  align-items: center;
}

/* 登录卡片 */
.login-card {
  padding: 0;
  border: 1px solid var(--border-color);
  overflow: hidden;
  box-shadow: var(--shadow-xl);
}

.card-header {
  padding: var(--space-10) var(--space-8);
  background: linear-gradient(135deg, var(--neutral-900) 0%, var(--neutral-800) 100%);
  color: white;
  text-align: center;
}

.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-3);
}

.logo-icon {
  width: 56px;
  height: 56px;
  color: white;
  opacity: 0.9;
}

.logo-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  margin: 0;
  letter-spacing: var(--tracking-tight);
}

.logo-subtitle {
  font-size: var(--text-base);
  opacity: 0.8;
  margin: 0;
}

.card-content {
  padding: var(--space-10) var(--space-8);
}

/* 错误消息 */
.alert {
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  text-align: center;
  margin-bottom: var(--space-6);
  font-weight: var(--font-medium);
}

.alert-error {
  background: var(--error-50);
  color: var(--error-600);
}

/* 登录表单 */
.login-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.form-label {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--neutral-700);
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: var(--space-3);
  width: 18px;
  height: 18px;
  color: var(--neutral-400);
  pointer-events: none;
}

.form-input {
  width: 100%;
  padding: var(--space-3) var(--space-3) var(--space-3) var(--space-10);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  font-size: var(--text-base);
  transition: all var(--transition-base);
}

.form-input:focus {
  outline: none;
  border-color: var(--border-color-focus);
  box-shadow: 0 0 0 3px rgb(100 116 139 / 0.1);
}

/* 登录按钮 */
.login-button {
  width: 100%;
  padding: var(--space-3_5);
  background: var(--neutral-900);
  color: white;
  border: none;
  border-radius: var(--radius-lg);
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  cursor: pointer;
  transition: all var(--transition-base);
  margin-top: var(--space-2);
}

.login-button:hover {
  background: var(--neutral-800);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.login-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 提示信息 */
.tips-section {
  margin-top: var(--space-8);
  padding-top: var(--space-6);
  border-top: 1px solid var(--border-color);
  text-align: center;
}

.tip-text {
  font-size: var(--text-sm);
  color: var(--neutral-500);
  margin: var(--space-1) 0;
  line-height: var(--leading-relaxed);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: var(--space-4);
    align-items: stretch;
  }

  .page-title {
    text-align: center;
    font-size: var(--text-xl);
  }

  .main-content {
    padding: var(--space-8) 0;
  }

  .card-header {
    padding: var(--space-8) var(--space-6);
  }

  .card-content {
    padding: var(--space-8) var(--space-6);
  }

  .logo-icon {
    width: 48px;
    height: 48px;
  }

  .logo-title {
    font-size: var(--text-xl);
  }
}

@media (max-width: 480px) {
  .container {
    padding: 0 var(--space-4);
  }

  .card-header,
  .card-content {
    padding: var(--space-6);
  }

  .logo-icon {
    width: 40px;
    height: 40px;
  }

  .logo-title {
    font-size: var(--text-lg);
  }
}
</style>
