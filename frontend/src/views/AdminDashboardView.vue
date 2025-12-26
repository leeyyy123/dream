<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  getLogs,
  deleteLogs,
  adminGetEmotions,
  adminAddEmotion,
  adminDeleteEmotion,
  adminGetDreamTypes,
  adminAddDreamType,
  adminDeleteDreamType,
  getPublicDreams
} from '../services/api'
import {
  ArrowLeft,
  Delete,
  Refresh,
  Plus,
  Document,
  Histogram,
  ChatDotRound
} from '@element-plus/icons-vue'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const error = ref('')
const success = ref('')
const activeTab = ref('logs')

// 日志数据
const logs = ref([])
const logsPagination = ref({
  currentPage: 1,
  pageSize: 20,
  totalItems: 0,
  totalPages: 0
})
const logsFilters = ref({
  logType: '',
  startDate: '',
  endDate: ''
})
const selectedLogIds = ref([])

// 情绪和类型数据
const emotions = ref([])
const dreamTypes = ref([])
const showAddEmotionDialog = ref(false)
const showAddTypeDialog = ref(false)
const newEmotion = ref({ emotionName: '', color: '#64748b' })
const newType = ref({ typeName: '', color: '#64748b' })

// 公开梦境数据
const publicDreams = ref([])
const dreamsPagination = ref({
  currentPage: 1,
  pageSize: 20,
  totalItems: 0,
  totalPages: 0
})
const selectedDreamDetail = ref(null)
const showDreamDetail = ref(false)

// 日志类型选项
const logTypeOptions = [
  { value: '', label: '全部类型' },
  { value: 'register', label: '注册' },
  { value: 'login', label: '登录' },
  { value: 'create_dream', label: '创建梦境' },
  { value: 'update_dream', label: '更新梦境' },
  { value: 'delete_dream', label: '删除梦境' },
  { value: 'create_analysis', label: '创建分析' },
  { value: 'ai_chat', label: 'AI对话' }
]

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
      minute: '2-digit',
      second: '2-digit'
    })
  } catch (error) {
    return '未知时间'
  }
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

// 显示消息
const showMessage = (msg, isError = false) => {
  if (isError) {
    error.value = msg
    success.value = ''
  } else {
    success.value = msg
    error.value = ''
  }
  setTimeout(() => {
    error.value = ''
    success.value = ''
  }, 3000)
}

// 获取管理员token
const getAdminToken = () => {
  return localStorage.getItem('adminToken')
}

// ============ 日志相关 ============
const fetchLogs = async () => {
  loading.value = true
  try {
    const token = getAdminToken()
    if (!token) {
      router.push('/admin/login')
      return
    }

    const params = {
      page: logsPagination.value.currentPage,
      pageSize: logsPagination.value.pageSize,
      ...logsFilters.value
    }

    const response = await getLogs(token, params)

    if (response.Code === 200) {
      logs.value = response.Data.logs || []
      logsPagination.value = response.Data.pagination || logsPagination.value
      selectedLogIds.value = []
    } else {
      showMessage(response.Msg || '获取日志失败', true)
    }
  } catch (err) {
    console.error('获取日志失败:', err)
    showMessage('网络错误，请稍后重试', true)
  } finally {
    loading.value = false
  }
}

const handleDeleteLogs = async () => {
  if (selectedLogIds.value.length === 0) {
    showMessage('请选择要删除的日志', true)
    return
  }

  if (!confirm(`确定要删除选中的 ${selectedLogIds.value.length} 条日志吗？`)) {
    return
  }

  loading.value = true
  try {
    const token = getAdminToken()
    const response = await deleteLogs(selectedLogIds.value, token)

    if (response.Code === 200) {
      showMessage(`成功删除 ${response.Data.deletedCount} 条日志`)
      await fetchLogs()
    } else {
      showMessage(response.Msg || '删除日志失败', true)
    }
  } catch (err) {
    console.error('删除日志失败:', err)
    showMessage('网络错误，请稍后重试', true)
  } finally {
    loading.value = false
  }
}

const handleLogsPageChange = (page) => {
  logsPagination.value.currentPage = page
  fetchLogs()
}

const handleLogSelect = (logId) => {
  const index = selectedLogIds.value.indexOf(logId)
  if (index > -1) {
    selectedLogIds.value.splice(index, 1)
  } else {
    selectedLogIds.value.push(logId)
  }
}

const handleSelectAllLogs = () => {
  if (selectedLogIds.value.length === logs.value.length) {
    selectedLogIds.value = []
  } else {
    selectedLogIds.value = logs.value.map(log => log.LogID)
  }
}

const applyLogsFilter = () => {
  logsPagination.value.currentPage = 1
  fetchLogs()
}

const resetLogsFilter = () => {
  logsFilters.value = {
    logType: '',
    startDate: '',
    endDate: ''
  }
  logsPagination.value.currentPage = 1
  fetchLogs()
}

// ============ 情绪和类型相关 ============
const fetchEmotions = async () => {
  loading.value = true
  try {
    const token = getAdminToken()
    const response = await adminGetEmotions(token)

    if (response.Code === 200) {
      emotions.value = response.Data || []
    } else {
      showMessage(response.Msg || '获取情绪失败', true)
    }
  } catch (err) {
    console.error('获取情绪失败:', err)
    showMessage('网络错误，请稍后重试', true)
  } finally {
    loading.value = false
  }
}

const fetchDreamTypes = async () => {
  loading.value = true
  try {
    const token = getAdminToken()
    const response = await adminGetDreamTypes(token)

    if (response.Code === 200) {
      dreamTypes.value = response.Data || []
    } else {
      showMessage(response.Msg || '获取梦境类型失败', true)
    }
  } catch (err) {
    console.error('获取梦境类型失败:', err)
    showMessage('网络错误，请稍后重试', true)
  } finally {
    loading.value = false
  }
}

const handleAddEmotion = async () => {
  if (!newEmotion.value.emotionName.trim()) {
    showMessage('请输入情绪名称', true)
    return
  }

  if (!newEmotion.value.color) {
    showMessage('请选择颜色', true)
    return
  }

  loading.value = true
  try {
    const token = getAdminToken()
    const response = await adminAddEmotion(newEmotion.value, token)

    if (response.Code === 200) {
      showMessage('添加情绪成功')
      showAddEmotionDialog.value = false
      newEmotion.value = { emotionName: '', color: '#64748b' }
      await fetchEmotions()
    } else {
      showMessage(response.Msg || '添加情绪失败', true)
    }
  } catch (err) {
    console.error('添加情绪失败:', err)
    showMessage('网络错误，请稍后重试', true)
  } finally {
    loading.value = false
  }
}

const handleDeleteEmotion = async (emotionId) => {
  if (!confirm('确定要删除这个情绪吗？')) {
    return
  }

  loading.value = true
  try {
    const token = getAdminToken()
    const response = await adminDeleteEmotion(emotionId, token)

    if (response.Code === 200) {
      showMessage('删除情绪成功')
      await fetchEmotions()
    } else {
      showMessage(response.Msg || '删除情绪失败', true)
    }
  } catch (err) {
    console.error('删除情绪失败:', err)
    showMessage('网络错误，请稍后重试', true)
  } finally {
    loading.value = false
  }
}

const handleAddDreamType = async () => {
  if (!newType.value.typeName.trim()) {
    showMessage('请输入类型名称', true)
    return
  }

  if (!newType.value.color) {
    showMessage('请选择颜色', true)
    return
  }

  loading.value = true
  try {
    const token = getAdminToken()
    const response = await adminAddDreamType(newType.value, token)

    if (response.Code === 200) {
      showMessage('添加类型成功')
      showAddTypeDialog.value = false
      newType.value = { typeName: '', color: '#64748b' }
      await fetchDreamTypes()
    } else {
      showMessage(response.Msg || '添加类型失败', true)
    }
  } catch (err) {
    console.error('添加梦境类型失败:', err)
    showMessage('网络错误，请稍后重试', true)
  } finally {
    loading.value = false
  }
}

const handleDeleteDreamType = async (typeId) => {
  if (!confirm('确定要删除这个类型吗？')) {
    return
  }

  loading.value = true
  try {
    const token = getAdminToken()
    const response = await adminDeleteDreamType(typeId, token)

    if (response.Code === 200) {
      showMessage('删除类型成功')
      await fetchDreamTypes()
    } else {
      showMessage(response.Msg || '删除类型失败', true)
    }
  } catch (err) {
    console.error('删除梦境类型失败:', err)
    showMessage('网络错误，请稍后重试', true)
  } finally {
    loading.value = false
  }
}

// ============ 公开梦境相关 ============
const fetchPublicDreams = async () => {
  loading.value = true
  try {
    const token = getAdminToken()
    const params = {
      page: dreamsPagination.value.currentPage,
      pageSize: dreamsPagination.value.pageSize
    }

    const response = await getPublicDreams(token, params)

    if (response.Code === 200) {
      publicDreams.value = response.Data.dreams || []
      dreamsPagination.value = response.Data.pagination || dreamsPagination.value
    } else {
      showMessage(response.Msg || '获取公开梦境失败', true)
    }
  } catch (err) {
    console.error('获取公开梦境失败:', err)
    showMessage('网络错误，请稍后重试', true)
  } finally {
    loading.value = false
  }
}

const handleDreamsPageChange = (page) => {
  dreamsPagination.value.currentPage = page
  fetchPublicDreams()
}

const showDreamDetails = (dream) => {
  selectedDreamDetail.value = dream
  showDreamDetail.value = true
}

// ============ 通用 ============
const goBack = () => {
  // 清除管理员token
  localStorage.removeItem('adminToken')
  localStorage.removeItem('adminEmail')
  // 跳转到主登录页面
  router.push('/')
}

const handleTabChange = (tab) => {
  activeTab.value = tab
  if (tab === 'logs') {
    fetchLogs()
  } else if (tab === 'emotions') {
    fetchEmotions()
    fetchDreamTypes()
  } else if (tab === 'dreams') {
    fetchPublicDreams()
  }
}

// 组件挂载
onMounted(() => {
  const token = getAdminToken()
  if (!token) {
    router.push('/admin/login')
    return
  }
  fetchLogs()
})
</script>

<template>
  <div class="admin-dashboard">
    <!-- 头部 -->
    <header class="header">
      <div class="container">
        <div class="header-content">
          <button class="back-button" @click="goBack">
            <component :is="ArrowLeft" class="back-icon" />
            <span>退出登录</span>
          </button>
          <h1 class="page-title">管理后台</h1>
          <div style="width: 80px;"></div>
        </div>
      </div>
    </header>

    <!-- 主要内容 -->
    <main class="main-content">
      <div class="container">
        <!-- 成功/错误消息 -->
        <div v-if="success" class="alert alert-success">
          {{ success }}
        </div>
        <div v-if="error" class="alert alert-error">
          {{ error }}
        </div>

        <!-- 标签页导航 -->
        <div class="tabs-nav">
          <button
            class="tab-button"
            :class="{ active: activeTab === 'logs' }"
            @click="handleTabChange('logs')"
          >
            <component :is="Document" class="tab-icon" />
            <span>日志管理</span>
          </button>
          <button
            class="tab-button"
            :class="{ active: activeTab === 'emotions' }"
            @click="handleTabChange('emotions')"
          >
            <component :is="Histogram" class="tab-icon" />
            <span>情绪与类型</span>
          </button>
          <button
            class="tab-button"
            :class="{ active: activeTab === 'dreams' }"
            @click="handleTabChange('dreams')"
          >
            <component :is="ChatDotRound" class="tab-icon" />
            <span>公开梦境</span>
          </button>
        </div>

        <!-- 日志管理 -->
        <div v-if="activeTab === 'logs'" class="tab-content">
          <div class="content-header">
            <h2 class="content-title">日志管理</h2>
            <div class="header-actions">
              <button
                v-if="selectedLogIds.length > 0"
                class="spa-button-danger"
                @click="handleDeleteLogs"
                :disabled="loading"
              >
                <component :is="Delete" class="btn-icon" />
                <span>删除选中 ({{ selectedLogIds.length }})</span>
              </button>
              <button class="spa-button-secondary" @click="fetchLogs" :disabled="loading">
                <component :is="Refresh" class="btn-icon" />
                <span>刷新</span>
              </button>
            </div>
          </div>

          <!-- 筛选器 -->
          <div class="filter-section spa-card">
            <div class="filter-grid">
              <div class="filter-item">
                <label class="filter-label">日志类型</label>
                <select v-model="logsFilters.logType" class="spa-input">
                  <option
                    v-for="option in logTypeOptions"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
              </div>
              <div class="filter-item">
                <label class="filter-label">开始日期</label>
                <input
                  v-model="logsFilters.startDate"
                  type="date"
                  class="spa-input"
                />
              </div>
              <div class="filter-item">
                <label class="filter-label">结束日期</label>
                <input
                  v-model="logsFilters.endDate"
                  type="date"
                  class="spa-input"
                />
              </div>
            </div>
            <div class="filter-actions">
              <button class="spa-button-primary" @click="applyLogsFilter">
                应用筛选
              </button>
              <button class="spa-button-secondary" @click="resetLogsFilter">
                重置
              </button>
            </div>
          </div>

          <!-- 日志列表 -->
          <div class="logs-table-container spa-card">
            <table class="logs-table">
              <thead>
                <tr>
                  <th class="checkbox-column">
                    <input
                      type="checkbox"
                      :checked="selectedLogIds.length === logs.length && logs.length > 0"
                      @change="handleSelectAllLogs"
                    />
                  </th>
                  <th>ID</th>
                  <th>用户</th>
                  <th>类型</th>
                  <th>操作描述</th>
                  <th>IP地址</th>
                  <th>时间</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="logs.length === 0">
                  <td colspan="7" class="empty-message">暂无日志数据</td>
                </tr>
                <tr v-for="log in logs" :key="log.LogID">
                  <td class="checkbox-column">
                    <input
                      type="checkbox"
                      :checked="selectedLogIds.includes(log.LogID)"
                      @change="handleLogSelect(log.LogID)"
                    />
                  </td>
                  <td>{{ log.LogID }}</td>
                  <td>{{ log.UserName || '未知用户' }}</td>
                  <td>
                    <span class="log-type-badge" :class="`log-type-${log.LogType}`">
                      {{ log.LogType }}
                    </span>
                  </td>
                  <td>{{ log.ActionDescription }}</td>
                  <td>{{ log.IP }}</td>
                  <td>{{ formatDateTime(log.Timestamp) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 分页 -->
          <div class="pagination">
            <button
              class="pagination-button"
              :disabled="logsPagination.currentPage === 1 || loading"
              @click="handleLogsPageChange(logsPagination.currentPage - 1)"
            >
              上一页
            </button>
            <span class="pagination-info">
              第 {{ logsPagination.currentPage }} / {{ logsPagination.totalPages }} 页
              (共 {{ logsPagination.totalItems }} 条)
            </span>
            <button
              class="pagination-button"
              :disabled="logsPagination.currentPage === logsPagination.totalPages || loading"
              @click="handleLogsPageChange(logsPagination.currentPage + 1)"
            >
              下一页
            </button>
          </div>
        </div>

        <!-- 情绪与类型管理 -->
        <div v-if="activeTab === 'emotions'" class="tab-content">
          <div class="two-column-layout">
            <!-- 情绪管理 -->
            <div class="column">
              <div class="column-header">
                <h2 class="content-title">情绪管理</h2>
                <button class="spa-button-primary" @click="showAddEmotionDialog = true">
                  <component :is="Plus" class="btn-icon" />
                  <span>添加情绪</span>
                </button>
              </div>

              <div class="items-list spa-card">
                <div v-if="emotions.length === 0" class="empty-message">暂无情绪数据</div>
                <div v-for="emotion in emotions" :key="emotion.EmotionID" class="item-card">
                  <div class="item-color-preview" :style="{ backgroundColor: emotion.Color }"></div>
                  <div class="item-info">
                    <h3 class="item-name">{{ emotion.EmotionName }}</h3>
                    <p class="item-color">{{ emotion.Color }}</p>
                  </div>
                  <button
                    class="item-delete-btn"
                    @click="handleDeleteEmotion(emotion.EmotionID)"
                  >
                    <component :is="Delete" class="btn-icon" />
                  </button>
                </div>
              </div>
            </div>

            <!-- 梦境类型管理 -->
            <div class="column">
              <div class="column-header">
                <h2 class="content-title">类型管理</h2>
                <button class="spa-button-primary" @click="showAddTypeDialog = true">
                  <component :is="Plus" class="btn-icon" />
                  <span>添加类型</span>
                </button>
              </div>

              <div class="items-list spa-card">
                <div v-if="dreamTypes.length === 0" class="empty-message">暂无类型数据</div>
                <div v-for="type in dreamTypes" :key="type.TypeID" class="item-card">
                  <div class="item-color-preview" :style="{ backgroundColor: type.Color }"></div>
                  <div class="item-info">
                    <h3 class="item-name">{{ type.TypeName }}</h3>
                    <p class="item-color">{{ type.Color }}</p>
                  </div>
                  <button
                    class="item-delete-btn"
                    @click="handleDeleteDreamType(type.TypeID)"
                  >
                    <component :is="Delete" class="btn-icon" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 公开梦境 -->
        <div v-if="activeTab === 'dreams'" class="tab-content">
          <div class="content-header">
            <h2 class="content-title">公开梦境</h2>
          </div>

          <div class="dreams-grid">
            <div v-if="publicDreams.length === 0" class="empty-message">暂无公开梦境</div>
            <div
              v-for="dream in publicDreams"
              :key="dream.DreamID"
              class="dream-card spa-card"
              @click="showDreamDetails(dream)"
            >
              <h3 class="dream-title">{{ dream.Title || '无标题' }}</h3>
              <p class="dream-user">用户: {{ dream.UserName }}</p>
              <p class="dream-date">日期: {{ formatDate(dream.DreamDate) }}</p>
              <div class="dream-emotions">
                <span
                  v-for="emotion in dream.Emotions"
                  :key="emotion.EmotionID"
                  class="emotion-tag"
                  :style="{ backgroundColor: emotion.Color + '20', color: emotion.Color }"
                >
                  {{ emotion.EmotionName }}
                </span>
              </div>
            </div>
          </div>

          <!-- 分页 -->
          <div class="pagination">
            <button
              class="pagination-button"
              :disabled="dreamsPagination.currentPage === 1 || loading"
              @click="handleDreamsPageChange(dreamsPagination.currentPage - 1)"
            >
              上一页
            </button>
            <span class="pagination-info">
              第 {{ dreamsPagination.currentPage }} / {{ dreamsPagination.totalPages }} 页
              (共 {{ dreamsPagination.totalItems }} 条)
            </span>
            <button
              class="pagination-button"
              :disabled="dreamsPagination.currentPage === dreamsPagination.totalPages || loading"
              @click="handleDreamsPageChange(dreamsPagination.currentPage + 1)"
            >
              下一页
            </button>
          </div>
        </div>
      </div>
    </main>

    <!-- 添加情绪对话框 -->
    <div v-if="showAddEmotionDialog" class="dialog-overlay" @click.self="showAddEmotionDialog = false">
      <div class="dialog-content spa-card">
        <h3 class="dialog-title">添加新情绪</h3>
        <div class="dialog-form">
          <div class="form-group">
            <label class="form-label">情绪名称</label>
            <input
              v-model="newEmotion.emotionName"
              type="text"
              class="spa-input"
              placeholder="请输入情绪名称"
              maxlength="20"
            />
          </div>
          <div class="form-group">
            <label class="form-label">颜色</label>
            <div class="color-picker-wrapper">
              <input
                v-model="newEmotion.color"
                type="color"
                class="color-picker"
              />
              <input
                v-model="newEmotion.color"
                type="text"
                class="spa-input color-input"
                placeholder="#64748b"
                maxlength="7"
              />
            </div>
          </div>
        </div>
        <div class="dialog-actions">
          <button class="spa-button-secondary" @click="showAddEmotionDialog = false">
            取消
          </button>
          <button class="spa-button-primary" @click="handleAddEmotion" :disabled="loading">
            {{ loading ? '添加中...' : '添加' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 添加类型对话框 -->
    <div v-if="showAddTypeDialog" class="dialog-overlay" @click.self="showAddTypeDialog = false">
      <div class="dialog-content spa-card">
        <h3 class="dialog-title">添加新类型</h3>
        <div class="dialog-form">
          <div class="form-group">
            <label class="form-label">类型名称</label>
            <input
              v-model="newType.typeName"
              type="text"
              class="spa-input"
              placeholder="请输入类型名称"
              maxlength="20"
            />
          </div>
          <div class="form-group">
            <label class="form-label">颜色</label>
            <div class="color-picker-wrapper">
              <input
                v-model="newType.color"
                type="color"
                class="color-picker"
              />
              <input
                v-model="newType.color"
                type="text"
                class="spa-input color-input"
                placeholder="#64748b"
                maxlength="7"
              />
            </div>
          </div>
        </div>
        <div class="dialog-actions">
          <button class="spa-button-secondary" @click="showAddTypeDialog = false">
            取消
          </button>
          <button class="spa-button-primary" @click="handleAddDreamType" :disabled="loading">
            {{ loading ? '添加中...' : '添加' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 梦境详情对话框 -->
    <div v-if="showDreamDetail && selectedDreamDetail" class="dialog-overlay dialog-large" @click.self="showDreamDetail = false">
      <div class="dialog-content dialog-content-large spa-card">
        <div class="dialog-header">
          <h3 class="dialog-title">{{ selectedDreamDetail.Title || '无标题' }}</h3>
          <button class="dialog-close" @click="showDreamDetail = false">×</button>
        </div>
        <div class="dialog-body">
          <div class="detail-row">
            <span class="detail-label">用户:</span>
            <span class="detail-value">{{ selectedDreamDetail.UserName }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">梦境日期:</span>
            <span class="detail-value">{{ formatDate(selectedDreamDetail.DreamDate) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">记录时间:</span>
            <span class="detail-value">{{ formatDateTime(selectedDreamDetail.RecordTime) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">睡眠质量:</span>
            <span class="detail-value">{{ selectedDreamDetail.SleepQuality || '未设置' }}/5</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">清晰度:</span>
            <span class="detail-value">{{ selectedDreamDetail.LucidityLevel || '未设置' }}/5</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">情绪:</span>
            <div class="detail-emotions">
              <span
                v-for="emotion in selectedDreamDetail.Emotions"
                :key="emotion.EmotionID"
                class="emotion-tag"
                :style="{ backgroundColor: emotion.Color + '20', color: emotion.Color }"
              >
                {{ emotion.EmotionName }}
              </span>
            </div>
          </div>
          <div class="detail-row">
            <span class="detail-label">类型:</span>
            <div class="detail-types">
              <span
                v-for="type in selectedDreamDetail.DreamTypes"
                :key="type.TypeID"
                class="type-tag"
                :style="{ backgroundColor: type.Color + '20', color: type.Color }"
              >
                {{ type.TypeName }}
              </span>
            </div>
          </div>
          <div class="detail-content">
            <h4 class="detail-content-title">梦境内容</h4>
            <p class="detail-content-text">{{ selectedDreamDetail.Content }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 基础样式 */
.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 var(--space-6);
}

/* 头部 */
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

.btn-icon {
  width: 16px;
  height: 16px;
}

/* 主内容 */
.main-content {
  padding: var(--space-8) 0;
}

/* 成功/错误消息 */
.alert {
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  text-align: center;
  margin-bottom: var(--space-6);
  font-weight: var(--font-medium);
}

.alert-success {
  background: var(--success-50);
  color: var(--success-600);
}

.alert-error {
  background: var(--error-50);
  color: var(--error-600);
}

/* 标签页导航 */
.tabs-nav {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-8);
  background: var(--neutral-100);
  padding: var(--space-1);
  border-radius: var(--radius-xl);
}

.tab-button {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  background: transparent;
  border: none;
  border-radius: var(--radius-lg);
  color: var(--neutral-600);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all var(--transition-base);
}

.tab-button:hover {
  color: var(--neutral-900);
}

.tab-button.active {
  background: white;
  color: var(--neutral-900);
  box-shadow: var(--shadow-sm);
}

.tab-icon {
  width: 18px;
  height: 18px;
}

/* 标签页内容 */
.tab-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);
}

.content-title {
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  color: var(--neutral-900);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: var(--space-3);
}

/* 按钮样式 */
.spa-button-primary,
.spa-button-secondary,
.spa-button-danger {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2_5) var(--space-4);
  border: none;
  border-radius: var(--radius-lg);
  cursor: pointer;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  transition: all var(--transition-base);
}

.spa-button-primary {
  background: var(--neutral-900);
  color: white;
}

.spa-button-primary:hover {
  background: var(--neutral-800);
  box-shadow: var(--shadow-md);
}

.spa-button-secondary {
  background: white;
  color: var(--neutral-700);
  border: 1px solid var(--border-color);
}

.spa-button-secondary:hover {
  background: var(--neutral-50);
  border-color: var(--border-color-hover);
  color: var(--neutral-900);
}

.spa-button-danger {
  background: var(--error-600);
  color: white;
}

.spa-button-danger:hover {
  background: var(--error-700);
}

.spa-button-primary:disabled,
.spa-button-secondary:disabled,
.spa-button-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spa-input {
  padding: var(--space-2_5) var(--space-3);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  font-size: var(--text-base);
  width: 100%;
}

.spa-input:focus {
  outline: none;
  border-color: var(--border-color-focus);
  box-shadow: 0 0 0 3px rgb(100 116 139 / 0.1);
}

.spa-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
}

/* 筛选器 */
.filter-section {
  margin-bottom: var(--space-6);
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.filter-label {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--neutral-700);
}

.filter-actions {
  display: flex;
  gap: var(--space-3);
  justify-content: flex-end;
}

/* 日志表格 */
.logs-table-container {
  overflow-x: auto;
  margin-bottom: var(--space-6);
}

.logs-table {
  width: 100%;
  border-collapse: collapse;
}

.logs-table th,
.logs-table td {
  padding: var(--space-3) var(--space-4);
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.logs-table th {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--neutral-700);
  background: var(--neutral-50);
}

.logs-table td {
  font-size: var(--text-sm);
  color: var(--neutral-900);
}

.checkbox-column {
  width: 40px;
  text-align: center;
}

.empty-message {
  text-align: center;
  padding: var(--space-12);
  color: var(--neutral-500);
  font-size: var(--text-base);
}

.log-type-badge {
  display: inline-block;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-md);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  background: var(--neutral-200);
  color: var(--neutral-700);
}

/* 分页 */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-4);
}

.pagination-button {
  padding: var(--space-2) var(--space-4);
  background: white;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  cursor: pointer;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  transition: all var(--transition-base);
}

.pagination-button:hover:not(:disabled) {
  background: var(--neutral-50);
  border-color: var(--border-color-hover);
}

.pagination-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  font-size: var(--text-sm);
  color: var(--neutral-600);
}

/* 两列布局 */
.two-column-layout {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: var(--space-8);
}

.column {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.items-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.item-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4);
  background: var(--neutral-50);
  border-radius: var(--radius-lg);
  transition: all var(--transition-base);
}

.item-card:hover {
  background: var(--neutral-100);
}

.item-color-preview {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-lg);
  border: 2px solid white;
  box-shadow: var(--shadow-sm);
  flex-shrink: 0;
}

.item-info {
  flex: 1;
}

.item-name {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--neutral-900);
  margin: 0 0 var(--space-1) 0;
}

.item-color {
  font-size: var(--text-sm);
  color: var(--neutral-600);
  font-family: monospace;
  margin: 0;
}

.item-delete-btn {
  padding: var(--space-2);
  background: transparent;
  border: none;
  border-radius: var(--radius-lg);
  color: var(--error-600);
  cursor: pointer;
  transition: all var(--transition-base);
}

.item-delete-btn:hover {
  background: var(--error-50);
}

/* 梦境网格 */
.dreams-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-6);
  margin-bottom: var(--space-6);
}

.dream-card {
  cursor: pointer;
  transition: all var(--transition-base);
  padding: var(--space-5);
}

.dream-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.dream-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--neutral-900);
  margin: 0 0 var(--space-2) 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dream-user,
.dream-date {
  font-size: var(--text-sm);
  color: var(--neutral-600);
  margin: 0 0 var(--space-1) 0;
}

.dream-emotions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-top: var(--space-3);
}

.emotion-tag,
.type-tag {
  display: inline-block;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-md);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
}

/* 对话框 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: var(--space-4);
}

.dialog-content {
  width: 100%;
  max-width: 450px;
  max-height: 90vh;
  overflow-y: auto;
}

.dialog-content-large {
  max-width: 700px;
}

.dialog-title {
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  color: var(--neutral-900);
  margin: 0 0 var(--space-6) 0;
}

.dialog-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
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

.color-picker-wrapper {
  display: flex;
  gap: var(--space-3);
  align-items: center;
}

.color-picker {
  width: 50px;
  height: 40px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  cursor: pointer;
  padding: 0;
}

.color-input {
  flex: 1;
}

.dialog-actions {
  display: flex;
  gap: var(--space-3);
  justify-content: flex-end;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--border-color);
}

.dialog-close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--radius-lg);
  font-size: var(--text-2xl);
  color: var(--neutral-500);
  cursor: pointer;
  transition: all var(--transition-base);
}

.dialog-close:hover {
  background: var(--neutral-100);
  color: var(--neutral-900);
}

.dialog-body {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.detail-row {
  display: flex;
  gap: var(--space-3);
  align-items: flex-start;
}

.detail-label {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--neutral-700);
  min-width: 80px;
}

.detail-value {
  font-size: var(--text-sm);
  color: var(--neutral-900);
}

.detail-emotions,
.detail-types {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.detail-content {
  margin-top: var(--space-4);
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-color);
}

.detail-content-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--neutral-900);
  margin: 0 0 var(--space-3) 0;
}

.detail-content-text {
  font-size: var(--text-sm);
  color: var(--neutral-700);
  line-height: var(--leading-relaxed);
  white-space: pre-wrap;
  margin: 0;
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

  .tabs-nav {
    flex-direction: column;
  }

  .two-column-layout {
    grid-template-columns: 1fr;
  }

  .dreams-grid {
    grid-template-columns: 1fr;
  }

  .filter-grid {
    grid-template-columns: 1fr;
  }

  .content-header {
    flex-direction: column;
    gap: var(--space-4);
    align-items: stretch;
  }

  .header-actions {
    flex-direction: column;
  }

  .dialog-content {
    max-width: 100%;
  }
}
</style>
