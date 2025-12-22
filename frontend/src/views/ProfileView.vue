<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getUserInfo, updateUserInfo, uploadAvatar } from '../services/api'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const editing = ref(false)
const saving = ref(false)
const error = ref('')
const success = ref('')
const uploading = ref(false)

// 用户信息数据
const userInfo = ref({
  userName: '',
  email: '',
  gender: '',
  birthDate: '',
  phone: '',
  address: '',
  avatar: null,
  createdAt: ''
})

// 编辑表单数据
const editForm = ref({
  userName: '',
  gender: '',
  birthDate: '',
  phone: '',
  address: ''
})

// 性别选项
const genderOptions = [
  { value: '', label: '请选择' },
  { value: 'male', label: '男' },
  { value: 'female', label: '女' },
  { value: 'other', label: '其他' }
]

// 返回主页
const goBack = () => {
  router.push('/main/home')
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '未知日期'

  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) return '未知日期'

    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    })
  } catch (error) {
    return '未知日期'
  }
}

// 格式化日期时间
const formatDateTime = (dateString) => {
  if (!dateString) return '未知时间'

  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) return '未知时间'

    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return '未知时间'
  }
}

// 获取用户信息
const fetchUserInfo = async () => {
  loading.value = true
  error.value = ''

  try {
    const token = localStorage.getItem('authToken')
    if (!token) {
      router.push('/')
      return
    }

    const response = await getUserInfo(token)

    if (response.Code === 200 && response.Data) {
      userInfo.value = {
        userName: response.Data.UserName || '',
        email: response.Data.Email || '',
        gender: response.Data.Gender || '',
        birthDate: response.Data.BirthDate || '',
        phone: response.Data.Phone || '',
        address: response.Data.Address || '',
        avatar: response.Data.AvatarUrl || null,
        createdAt: response.Data.CreatedAt || ''
      }

      // 初始化编辑表单
      editForm.value = {
        userName: userInfo.value.userName,
        gender: userInfo.value.gender,
        birthDate: userInfo.value.birthDate,
        phone: userInfo.value.phone,
        address: userInfo.value.address
      }
    } else {
      error.value = response.Msg || '获取用户信息失败'
    }
  } catch (err) {
    console.error('获取用户信息失败:', err)
    error.value = '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 开始编辑
const startEditing = () => {
  editing.value = true
  error.value = ''
  success.value = ''

  // 重置编辑表单
  editForm.value = {
    userName: userInfo.value.userName,
    gender: userInfo.value.gender,
    birthDate: userInfo.value.birthDate,
    phone: userInfo.value.phone,
    address: userInfo.value.address
  }
}

// 取消编辑
const cancelEditing = () => {
  editing.value = false
  error.value = ''
  success.value = ''

  // 重置编辑表单
  editForm.value = {
    userName: userInfo.value.userName,
    gender: userInfo.value.gender,
    birthDate: userInfo.value.birthDate,
    phone: userInfo.value.phone,
    address: userInfo.value.address
  }
}

// 保存个人信息
const saveProfile = async () => {
  if (!editForm.value.userName.trim()) {
    error.value = '用户名不能为空'
    return
  }

  saving.value = true
  error.value = ''
  success.value = ''

  try {
    const token = localStorage.getItem('authToken')
    const response = await updateUserInfo(editForm.value, token)

    if (response.Code === 200) {
      userInfo.value = {
        ...userInfo.value,
        userName: editForm.value.userName,
        gender: editForm.value.gender,
        birthDate: editForm.value.birthDate,
        phone: editForm.value.phone,
        address: editForm.value.address
      }

      editing.value = false
      success.value = '个人信息更新成功'

      // 3秒后清除成功消息
      setTimeout(() => {
        success.value = ''
      }, 3000)
    } else {
      error.value = response.Msg || '更新个人信息失败'
    }
  } catch (err) {
    console.error('更新个人信息失败:', err)
    error.value = '网络错误，请稍后重试'
  } finally {
    saving.value = false
  }
}

// 上传头像
const handleAvatarUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  // 验证文件类型
  if (!file.type.startsWith('image/')) {
    error.value = '请选择图片文件'
    return
  }

  // 验证文件大小 (5MB)
  if (file.size > 5 * 1024 * 1024) {
    error.value = '图片大小不能超过5MB'
    return
  }

  uploading.value = true
  error.value = ''

  try {
    const token = localStorage.getItem('authToken')
    const formData = new FormData()
    formData.append('avatar', file)

    const response = await uploadAvatar(formData, token)

    if (response.Code === 200) {
      userInfo.value.avatar = response.Data?.AvatarUrl || null
      success.value = '头像上传成功'

      // 3秒后清除成功消息
      setTimeout(() => {
        success.value = ''
      }, 3000)
    } else {
      error.value = response.Msg || '头像上传失败'
    }
  } catch (err) {
    console.error('头像上传失败:', err)
    error.value = '网络错误，请稍后重试'
  } finally {
    uploading.value = false
  }

  // 清空文件输入
  event.target.value = ''
}

// 组件挂载
onMounted(() => {
  fetchUserInfo()
})
</script>

<template>
  <div class="profile-container">
    <!-- 头部 -->
    <header class="header">
      <div class="container">
        <div class="header-content">
          <button class="back-button" @click="goBack">
            ←
            <span>返回</span>
          </button>
          <h1 class="page-title">个人信息</h1>
          <button v-if="!editing" class="btn-primary" @click="startEditing">
            ✏️
            <span>编辑</span>
          </button>
        </div>
      </div>
    </header>

    <!-- 主要内容 -->
    <main class="main-content">
      <div class="container">
        <!-- 成功/错误消息 -->
        <div v-if="success" class="success-message">
          {{ success }}
        </div>
        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-section">
          <div class="loading-spinner"></div>
          <span>加载中...</span>
        </div>

        <!-- 用户信息 -->
        <div v-else class="profile-content">
          <!-- 头像区域 -->
          <div class="avatar-section">
            <div class="avatar-container">
              <img
                v-if="userInfo.avatar"
                :src="userInfo.avatar"
                :alt="userInfo.userName"
                class="avatar-img"
              />
              <div v-else class="default-avatar">
                👤
              </div>

              <!-- 头像上传按钮 -->
              <label class="avatar-upload" :class="{ uploading }">
                <input
                  type="file"
                  accept="image/*"
                  @change="handleAvatarUpload"
                  :disabled="uploading"
                />
                📷
              </label>
            </div>
            <h2 class="username">{{ userInfo.userName || '未设置用户名' }}</h2>
            <p class="email">{{ userInfo.email }}</p>
          </div>

          <!-- 信息卡片 -->
          <div class="info-card" style="background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div class="card-header">
              <h3 class="card-title">基本信息</h3>
            </div>

            <div class="card-content">
              <!-- 只读模式 -->
              <div v-if="!editing" class="info-grid">
                <div class="info-item">
                  <label class="info-label">用户名</label>
                  <p class="info-value">{{ userInfo.userName || '未设置' }}</p>
                </div>

                <div class="info-item">
                  <label class="info-label">邮箱</label>
                  <p class="info-value">{{ userInfo.email }}</p>
                </div>

                <div class="info-item">
                  <label class="info-label">性别</label>
                  <p class="info-value">{{ genderOptions.find(g => g.value === userInfo.gender)?.label || '未设置' }}</p>
                </div>

                <div class="info-item">
                  <label class="info-label">出生日期</label>
                  <p class="info-value">{{ formatDate(userInfo.birthDate) || '未设置' }}</p>
                </div>

                <div class="info-item">
                  <label class="info-label">手机号</label>
                  <p class="info-value">{{ userInfo.phone || '未设置' }}</p>
                </div>

                <div class="info-item">
                  <label class="info-label">地址</label>
                  <p class="info-value">{{ userInfo.address || '未设置' }}</p>
                </div>

                <div class="info-item">
                  <label class="info-label">注册时间</label>
                  <p class="info-value">{{ formatDateTime(userInfo.createdAt) }}</p>
                </div>
              </div>

              <!-- 编辑模式 -->
              <form v-else class="edit-form" @submit.prevent="saveProfile">
                <div class="form-grid">
                  <div class="form-group">
                    <label class="form-label">用户名</label>
                    <input
                      v-model="editForm.userName"
                      type="text"
                      class="form-input"
                      placeholder="请输入用户名"
                      maxlength="50"
                    />
                  </div>

                  <div class="form-group">
                    <label class="form-label">邮箱</label>
                    <input
                      type="email"
                      class="form-input"
                      :value="userInfo.email"
                      disabled
                      style="background: var(--neutral-100); color: var(--neutral-500);"
                    />
                    <p class="form-help">邮箱地址不可修改</p>
                  </div>

                  <div class="form-group">
                    <label class="form-label">性别</label>
                    <select v-model="editForm.gender" class="spa-input">
                      <option
                        v-for="option in genderOptions"
                        :key="option.value"
                        :value="option.value"
                      >
                        {{ option.label }}
                      </option>
                    </select>
                  </div>

                  <div class="form-group">
                    <label class="form-label">出生日期</label>
                    <input
                      v-model="editForm.birthDate"
                      type="date"
                      class="form-input"
                      :max="new Date().toISOString().split('T')[0]"
                    />
                  </div>

                  <div class="form-group">
                    <label class="form-label">手机号</label>
                    <input
                      v-model="editForm.phone"
                      type="tel"
                      class="form-input"
                      placeholder="请输入手机号"
                      maxlength="11"
                    />
                  </div>

                  <div class="form-group">
                    <label class="form-label">地址</label>
                    <textarea
                      v-model="editForm.address"
                      class="form-input textarea"
                      placeholder="请输入地址"
                      rows="3"
                      maxlength="200"
                    ></textarea>
                  </div>
                </div>

                <!-- 操作按钮 -->
                <div class="form-actions">
                  <button
                    type="button"
                    class="btn-secondary"
                    @click="cancelEditing"
                    :disabled="saving"
                  >
                    取消
                  </button>
                  <button
                    type="submit"
                    class="btn-primary"
                    :disabled="saving"
                  >
                    {{ saving ? '保存中...' : '保存' }}
                  </button>
                </div>
              </form>
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
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.btn-primary {
  background: #667eea;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-primary:hover {
  background: #5a67d8;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f8f8f8;
  color: #333;
  border: 1px solid #ddd;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.btn-secondary:hover {
  background: #e8e8e8;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
}

.form-input.textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
  line-height: 1.5;
}

.profile-container {
  min-height: 100vh;
  background: #f5f5f5;
}

/* 头部样式 */
.header {
  background: white;
  border-bottom: 1px solid var(--border-color);
  padding: 24px 0;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 24px;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: var(--space-3) 16px;
  background: transparent;
  border: none;
  border-radius: var(--radius-lg);
  color: var(--neutral-700);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-base);
}

.back-button:hover {
  background: var(--neutral-100);
  color: var(--neutral-900);
}

.page-title {
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--neutral-900);
  margin: 0;
  flex: 1;
}

.spa-button-primary {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 主内容区域 */
.main-content {
  padding: 32px 0;
}

/* 成功/错误消息 */
.success-message {
  background: var(--success-50);
  color: var(--success-600);
  padding: 16px;
  border-radius: var(--radius-lg);
  text-align: center;
  margin-bottom: 24px;
  font-weight: 500;
}

.error-message {
  background: var(--error-50);
  color: var(--error-600);
  padding: 16px;
  border-radius: var(--radius-lg);
  text-align: center;
  margin-bottom: 24px;
  font-weight: 500;
}

/* 加载状态 */
.loading-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-20) 16px;
  color: var(--neutral-500);
  font-size: var(--text-lg);
  gap: 16px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--neutral-200);
  border-top: 3px solid var(--primary-500);
  border-radius: var(--radius-full);
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 个人资料内容 */
.profile-content {
  max-width: 800px;
  margin: 0 auto;
}

/* 头像区域 */
.avatar-section {
  text-align: center;
  margin-bottom: var(--space-12);
}

.avatar-container {
  position: relative;
  display: inline-block;
  margin-bottom: 16px;
}

.avatar-img {
  width: 120px;
  height: 120px;
  border-radius: var(--radius-full);
  object-fit: cover;
  border: 4px solid white;
  box-shadow: var(--shadow-lg);
}

.default-avatar {
  width: 120px;
  height: 120px;
  background: var(--neutral-200);
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--neutral-400);
  border: 4px solid white;
  box-shadow: var(--shadow-lg);
}

.avatar-upload {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 36px;
  height: 36px;
  background: var(--primary-500);
  color: white;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-base);
  box-shadow: var(--shadow-md);
  border: 3px solid white;
}

.avatar-upload:hover {
  background: var(--primary-600);
  transform: scale(1.1);
}

.avatar-upload.uploading {
  background: var(--neutral-400);
  cursor: not-allowed;
}

.avatar-upload input {
  display: none;
}

.username {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--neutral-900);
  margin: 0 0 4px 0;
}

.email {
  font-size: var(--text-base);
  color: var(--neutral-600);
  margin: 0;
}

/* 信息卡片 */
.info-card {
  background: white;
  border-radius: var(--radius-2xl);
  overflow: hidden;
}

.card-header {
  padding: 24px 32px;
  border-bottom: 1px solid var(--border-color);
  background: var(--neutral-50);
}

.card-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--neutral-900);
  margin: 0;
}

.card-content {
  padding: 32px;
}

/* 只读模式 - 信息网格 */
.info-grid {
  display: grid;
  gap: 32px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-label {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--neutral-600);
}

.info-value {
  font-size: var(--text-base);
  color: var(--neutral-900);
  margin: 0;
  font-weight: 500;
}

/* 编辑模式 - 表单 */
.edit-form {
  /* 表单样式 */
}

.form-grid {
  display: grid;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--neutral-700);
}

.spa-input {
  font-size: var(--text-base);
}

.spa-input.textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
  line-height: 1.5;
}

.form-help {
  font-size: var(--text-xs);
  color: var(--neutral-500);
  margin: 4px 0 0 0;
}

/* 操作按钮 */
.form-actions {
  display: flex;
  gap: 16px;
  justify-content: flex-end;
  padding-top: 32px;
  border-top: 1px solid var(--border-color);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .page-title {
    text-align: center;
    font-size: var(--text-2xl);
  }

  .avatar-img,
  .default-avatar {
    width: 100px;
    height: 100px;
  }

  .username {
    font-size: var(--text-xl);
  }

  .card-header,
  .card-content {
    padding: 24px;
  }

  .form-actions {
    flex-direction: column;
  }
}

@media (max-width: 480px) {
  .avatar-section {
    margin-bottom: 32px;
  }

  .card-header,
  .card-content {
    padding: 16px;
  }

  .form-grid {
    gap: 16px;
  }
}
</style>