<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDreamsList, deleteDream, getDreamDetail } from '../services/api'
import {
  Reading,
  Close,
  Edit,
  Delete,
  Search,
  DocumentAdd,
  Moon,
  Calendar,
  ArrowLeft,
  ChatLineRound
} from '@element-plus/icons-vue'

const router = useRouter()

// 响应式数据
const dreams = ref([])
const loading = ref(false)
const error = ref('')
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const totalCount = ref(0)
const showDeleteConfirm = ref(false)
const dreamToDelete = ref(null)

// 梦境详情弹窗相关
const showDreamDetail = ref(false)
const selectedDream = ref(null)

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// 获取睡眠质量文本
const getSleepQualityText = (quality) => {
  const qualityMap = {
    1: '很差',
    2: '较差',
    3: '一般',
    4: '较好',
    5: '很好'
  }
  return qualityMap[quality] || '未知'
}

// 获取梦境清晰度文本
const getLucidityText = (lucidity) => {
  const lucidityMap = {
    1: '非常模糊',
    2: '比较模糊',
    3: '一般',
    4: '比较清晰',
    5: '非常清晰'
  }
  return lucidityMap[lucidity] || '未知'
}

// 获取关键词分类的显示名称
const getCategoryName = (category) => {
  const categoryNames = {
    person: '人物',
    place: '地点',
    object: '物品',
    event: '事件',
    symbol: '象征',
    other: '其他'
  }
  return categoryNames[category] || '其他'
}

// 获取梦境列表
const fetchDreams = async () => {
  loading.value = true
  error.value = ''

  try {
    const token = localStorage.getItem('authToken')
    if (!token) {
      router.push('/')
      return
    }

    const response = await getDreamsList(token, {
      page: currentPage.value,
      pageSize: pageSize.value,
      keyword: searchKeyword.value
    })

    if (response.Code === 200) {
      if (response.Data && Array.isArray(response.Data)) {
        dreams.value = response.Data
      } else if (response.Data && response.Data.Dreams && Array.isArray(response.Data.Dreams)) {
        dreams.value = response.Data.Dreams
      } else if (response.Data && response.Data.dreams && Array.isArray(response.Data.dreams)) {
        dreams.value = response.Data.dreams
      } else if (Array.isArray(response)) {
        dreams.value = response
      } else {
        dreams.value = []
      }

      totalCount.value = response.Count || response.TotalCount || dreams.value.length || 0
    } else {
      error.value = response.Msg || '获取梦境列表失败'
    }
  } catch (err) {
    console.error('获取梦境列表失败:', err)
    error.value = '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 删除梦境
const confirmDelete = (dream) => {
  dreamToDelete.value = dream
  showDeleteConfirm.value = true
}

// 从详情弹窗删除梦境
const deleteFromDetail = () => {
  if (selectedDream.value) {
    confirmDelete(selectedDream.value)
  }
}

// 执行删除
const deleteDreamItem = async () => {
  if (!dreamToDelete.value) return

  try {
    const token = localStorage.getItem('authToken')
    const response = await deleteDream(dreamToDelete.value.DreamID, token)

    if (response.Code === 200) {
      await fetchDreams()
      showDeleteConfirm.value = false
      dreamToDelete.value = null
      closeDreamDetail()
    } else {
      alert(`删除失败: ${response.Msg}`)
    }
  } catch (err) {
    console.error('删除梦境失败:', err)
    alert('删除失败，请稍后重试')
  }
}

// 取消删除
const cancelDelete = () => {
  showDeleteConfirm.value = false
  dreamToDelete.value = null
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchDreams()
}

// 页码改变
const handlePageChange = (page) => {
  currentPage.value = page
  fetchDreams()
}

// 创建新梦境
const createNewDream = () => {
  router.push('/create-dream')
}

// 返回上一页
const goBack = () => {
  router.push('/main/home')
}

// 显示梦境详情
const showDreamDetails = async (dream) => {
  try {
    const token = localStorage.getItem('authToken')
    if (!token) {
      router.push('/')
      return
    }

    const response = await getDreamDetail(dream.DreamID, token)
    if (response.Code === 200 && response.Data) {
      selectedDream.value = response.Data
      showDreamDetail.value = true
    } else {
      alert(`获取梦境详情失败: ${response.Msg}`)
    }
  } catch (error) {
    console.error('获取梦境详情失败:', error)
    alert('获取梦境详情失败，请稍后重试')
  }
}

// 关闭梦境详情
const closeDreamDetail = () => {
  showDreamDetail.value = false
  selectedDream.value = null
}

// 编辑梦境
const editDream = (dreamId) => {
  closeDreamDetail()
  router.push(`/edit-dream/${dreamId}`)
}

// 问AI
const askAI = () => {
  const dreamId = selectedDream.value?.DreamID
  if (dreamId) {
    router.push({
      path: '/ai-chat',
      query: { source: 'dream', id: dreamId }
    })
  }
}

// 获取总页数
const totalPages = () => {
  return Math.ceil(totalCount.value / pageSize.value)
}

// 组件挂载
onMounted(() => {
  fetchDreams()
})
</script>

<template>
  <div class="my-dreams-container">
    <!-- 头部 -->
    <header class="header">
      <div class="spa-container">
        <div class="header-content">
          <button class="back-button" @click="goBack">
            <component :is="ArrowLeft" class="back-icon" />
            <span>返回</span>
          </button>
          <div class="header-left">
            <h1 class="page-title">我的梦境</h1>
            <p class="page-subtitle">共 {{ totalCount }} 个梦境记录</p>
          </div>
          <button class="spa-button-primary" @click="createNewDream">
            <component :is="DocumentAdd" class="btn-icon" />
            <span>记录新梦境</span>
          </button>
        </div>
      </div>
    </header>

    <!-- 主要内容 -->
    <main class="main-content">
      <div class="spa-container">
        <!-- 搜索栏 -->
        <div class="search-section">
          <div class="search-form">
            <div class="search-input-wrapper">
              <component :is="Search" class="search-icon" />
              <input
                v-model="searchKeyword"
                type="text"
                placeholder="搜索梦境标题或内容..."
                class="form-input search-input spa-input"
                @keyup.enter="handleSearch"
              />
              <button class="spa-button-primary search-button" @click="handleSearch">
                搜索
              </button>
            </div>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-section">
          <div class="loading-spinner"></div>
          <span>加载中...</span>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="error" class="error-section">
          <p class="error-message">{{ error }}</p>
          <button class="spa-button-primary" @click="fetchDreams">重试</button>
        </div>

        <!-- 梦境列表 -->
        <div v-else-if="dreams.length > 0" class="dreams-grid">
          <div
            v-for="dream in dreams"
            :key="dream.DreamID"
            class="dream-card spa-card clickable"
            @click="showDreamDetails(dream)"
          >
            <div class="dream-header">
              <div class="dream-icon">
                <component :is="Reading" />
              </div>
              <div class="dream-meta">
                <h3 class="dream-title">{{ dream.Title }}</h3>
                <p class="dream-date">{{ formatDate(dream.DreamDate) }}</p>
              </div>
            </div>

            <div class="dream-content">
              <p class="dream-text">{{ dream.Content }}</p>
            </div>

            <div class="dream-stats">
              <div class="stat-item">
                <span class="stat-label">睡眠质量</span>
                <span class="stat-value">{{ getSleepQualityText(dream.SleepQuality) }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">梦境清晰度</span>
                <span class="stat-value">{{ getLucidityText(dream.LucidityLevel) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="empty-state">
          <div class="empty-icon">
            <component :is="Moon" />
          </div>
          <h3 class="empty-title">还没有梦境记录</h3>
          <p class="empty-description">开始记录你的第一个梦境吧</p>
          <button class="spa-button-primary" @click="createNewDream">
            记录梦境
          </button>
        </div>

        <!-- 分页 -->
        <div v-if="dreams.length > 0 && totalPages() > 1" class="pagination">
          <button
            :disabled="currentPage === 1"
            class="spa-button-secondary"
            @click="handlePageChange(currentPage - 1)"
          >
            上一页
          </button>

          <span class="page-info">
            第 {{ currentPage }} 页，共 {{ totalPages() }} 页
          </span>

          <button
            :disabled="currentPage === totalPages()"
            class="spa-button-secondary"
            @click="handlePageChange(currentPage + 1)"
          >
            下一页
          </button>
        </div>
      </div>
    </main>

    <!-- 删除确认弹窗 -->
    <div v-if="showDeleteConfirm" class="modal-overlay delete-modal" @click="cancelDelete">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">确认删除</h2>
          <button class="modal-close" @click="cancelDelete">
            <component :is="Close" class="close-icon" />
          </button>
        </div>
        <div class="modal-body">
          <p>确定要删除梦境《{{ dreamToDelete?.Title }}》吗？此操作不可撤销。</p>
        </div>
        <div class="modal-footer">
          <button class="spa-button-secondary" @click="cancelDelete">
            取消
          </button>
          <button class="spa-button-danger" @click="deleteDreamItem">
            删除
          </button>
        </div>
      </div>
    </div>

    <!-- 梦境详情弹窗 -->
    <div v-if="showDreamDetail && selectedDream" class="modal-overlay" @click="closeDreamDetail">
      <div class="modal dream-detail-modal" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">{{ selectedDream.Title }}</h2>
          <button class="modal-close" @click="closeDreamDetail">
            <component :is="Close" class="close-icon" />
          </button>
        </div>

        <div class="modal-body">
          <div class="dream-detail-content">
            <!-- 梦境基本信息 -->
            <div class="detail-section">
              <div class="detail-meta">
                <div class="detail-date">
                  <component :is="Calendar" class="detail-icon" />
                  <span class="detail-label">梦境日期:</span>
                  <span class="detail-value">{{ formatDate(selectedDream.DreamDate) }}</span>
                </div>
              </div>
            </div>

            <!-- 梦境内容 -->
            <div class="detail-section">
              <h3 class="section-title">梦境内容</h3>
              <div class="detail-content">
                {{ selectedDream.Content }}
              </div>
            </div>

            <!-- 情绪标签 -->
            <div v-if="selectedDream.Emotions && selectedDream.Emotions.length > 0" class="detail-section">
              <h3 class="section-title">情绪标签</h3>
              <div class="emotion-tags">
                <span
                  v-for="emotion in selectedDream.Emotions"
                  :key="emotion.EmotionID"
                  class="emotion-tag"
                  :style="{ backgroundColor: emotion.Color }"
                >
                  {{ emotion.EmotionName }}
                </span>
              </div>
            </div>

            <!-- 梦境类型 -->
            <div v-if="selectedDream.DreamTypes && selectedDream.DreamTypes.length > 0" class="detail-section">
              <h3 class="section-title">梦境类型</h3>
              <div class="type-tags">
                <span
                  v-for="type in selectedDream.DreamTypes"
                  :key="type.TypeID"
                  class="type-tag"
                  :style="{ backgroundColor: type.Color }"
                >
                  {{ type.TypeName }}
                </span>
              </div>
            </div>

            <!-- 关键词 -->
            <div v-if="selectedDream.Keywords && selectedDream.Keywords.length > 0" class="detail-section">
              <h3 class="section-title">关键词</h3>
              <div class="keyword-tags">
                <div
                  v-for="(keyword, index) in selectedDream.Keywords"
                  :key="index"
                  class="keyword-tag"
                >
                  <span class="keyword-text">{{ keyword.KeywordText }}</span>
                  <span class="keyword-category">{{ getCategoryName(keyword.Category) }}</span>
                </div>
              </div>
            </div>

            <!-- 梦境评估 -->
            <div class="detail-section">
              <h3 class="section-title">睡眠评估</h3>
              <div class="detail-stats">
                <div class="detail-stat">
                  <span class="detail-label">睡眠质量:</span>
                  <span class="detail-value">{{ getSleepQualityText(selectedDream.SleepQuality) }}</span>
                </div>
                <div class="detail-stat">
                  <span class="detail-label">梦境清晰度:</span>
                  <span class="detail-value">{{ getLucidityText(selectedDream.LucidityLevel) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <div class="detail-actions">
            <button class="spa-button-secondary ai-button" @click="askAI">
              <component :is="ChatLineRound" class="action-icon" />
              <span>问AI</span>
            </button>
            <button class="spa-button-primary" @click="editDream(selectedDream.DreamID)">
              <component :is="Edit" class="action-icon" />
              <span>编辑梦境</span>
            </button>
            <button class="spa-button-danger" @click="deleteFromDetail">
              <component :is="Delete" class="action-icon" />
              <span>删除梦境</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.my-dreams-container {
  min-height: 100vh;
  background: var(--neutral-50);
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
  flex-shrink: 0;
}

.back-button:hover {
  background: var(--neutral-100);
  color: var(--neutral-900);
}

.back-icon {
  width: 18px;
  height: 18px;
}

.header-left {
  flex: 1;
}

.page-title {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--neutral-900);
  margin: 0 0 var(--space-2) 0;
  line-height: var(--leading-tight);
  letter-spacing: var(--tracking-tight);
}

.page-subtitle {
  font-size: var(--text-base);
  color: var(--neutral-600);
  margin: 0;
}

/* 主内容区域 */
.main-content {
  padding: var(--space-8) 0;
}

/* 搜索区域 */
.search-section {
  margin-bottom: var(--space-8);
}

.search-form {
  max-width: 640px;
  margin: 0 auto;
}

.search-input-wrapper {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2);
  background: white;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-fast);
}

.search-input-wrapper:focus-within {
  border-color: var(--border-color-focus);
  box-shadow: 0 0 0 3px rgb(100 116 139 / 0.1);
}

.search-icon {
  width: 20px;
  height: 20px;
  color: var(--neutral-400);
  flex-shrink: 0;
  margin-left: var(--space-2);
}

.search-input {
  flex: 1;
  padding: var(--space-2_5) var(--space-2);
  border: none;
  background: transparent;
  font-size: var(--text-base);
}

.search-input:focus {
  outline: none;
  box-shadow: none;
}

.search-button {
  flex-shrink: 0;
  padding: var(--space-2_5) var(--space-5);
  font-size: var(--text-sm);
}

.btn-icon {
  width: 18px;
  height: 18px;
}

/* 按钮样式 */
.spa-button-primary {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2_5) var(--space-5);
  background: var(--neutral-900);
  color: white;
  border: none;
  border-radius: var(--radius-lg);
  cursor: pointer;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  transition: all var(--transition-base);
}

.spa-button-primary:hover {
  background: var(--neutral-800);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.spa-button-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.spa-button-secondary {
  padding: var(--space-2_5) var(--space-5);
  background: white;
  color: var(--neutral-700);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  cursor: pointer;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  transition: all var(--transition-base);
}

.spa-button-secondary:hover {
  background: var(--neutral-50);
  border-color: var(--border-color-hover);
  color: var(--neutral-900);
}

.spa-button-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.ai-button {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2_5) var(--space-5);
  background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
  color: white;
  border: none;
  border-radius: var(--radius-lg);
  cursor: pointer;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  transition: all var(--transition-base);
}

.ai-button:hover {
  background: linear-gradient(135deg, #0284c7 0%, #0891b2 100%);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.spa-button-danger {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2_5) var(--space-5);
  background: var(--error-500);
  color: white;
  border: none;
  border-radius: var(--radius-lg);
  cursor: pointer;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  transition: all var(--transition-base);
}

.spa-button-danger:hover {
  background: var(--error-600);
}

.action-icon {
  width: 16px;
  height: 16px;
}

/* 加载和错误状态 */
.loading-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-20) var(--space-4);
  color: var(--neutral-500);
  font-size: var(--text-lg);
  gap: var(--space-4);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--neutral-200);
  border-top: 3px solid var(--neutral-900);
  border-radius: var(--radius-full);
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-section {
  text-align: center;
  padding: var(--space-20) var(--space-4);
}

.error-message {
  color: var(--error-600);
  font-size: var(--text-lg);
  margin-bottom: var(--space-4);
}

/* 梦境网格 */
.dreams-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: var(--space-5);
  margin-bottom: var(--space-8);
}

.dream-card {
  padding: var(--space-5);
  border: 1px solid var(--border-color);
  transition: all var(--transition-base);
}

.dream-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--border-color-hover);
  transform: translateY(-1px);
}

.dream-card.clickable {
  cursor: pointer;
}

.dream-card.clickable:hover {
  box-shadow: var(--shadow-lg);
}

.dream-header {
  display: flex;
  align-items: flex-start;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

.dream-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: var(--neutral-100);
  color: var(--neutral-600);
  border-radius: var(--radius-lg);
  flex-shrink: 0;
}

.dream-icon > * {
  width: 20px;
  height: 20px;
}

.dream-meta {
  flex: 1;
  min-width: 0;
}

.dream-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--neutral-900);
  margin: 0 0 var(--space-1) 0;
  line-height: var(--leading-snug);
}

.dream-date {
  font-size: var(--text-sm);
  color: var(--neutral-500);
  margin: 0;
}

.dream-content {
  margin-bottom: var(--space-4);
}

.dream-text {
  font-size: var(--text-sm);
  color: var(--neutral-700);
  line-height: var(--leading-relaxed);
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.dream-stats {
  display: flex;
  gap: var(--space-5);
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-color);
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.stat-label {
  font-size: var(--text-xs);
  color: var(--neutral-500);
  font-weight: var(--font-medium);
}

.stat-value {
  font-size: var(--text-sm);
  color: var(--neutral-900);
  font-weight: var(--font-semibold);
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: var(--space-20) var(--space-4);
}

.empty-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  background: var(--neutral-100);
  border-radius: var(--radius-2xl);
  color: var(--neutral-400);
  margin: 0 auto var(--space-6);
}

.empty-icon > * {
  width: 32px;
  height: 32px;
}

.empty-title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--neutral-800);
  margin: 0 0 var(--space-2) 0;
}

.empty-description {
  font-size: var(--text-base);
  color: var(--neutral-600);
  margin: 0 0 var(--space-6) 0;
}

/* 分页 */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-4);
}

.page-info {
  font-size: var(--text-sm);
  color: var(--neutral-600);
  font-weight: var(--font-medium);
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
  padding: var(--space-4);
}

/* 删除确认弹窗需要更高的 z-index */
.modal-overlay.delete-modal {
  z-index: calc(var(--z-modal) + 100);
}

.modal {
  background: white;
  border-radius: var(--radius-2xl);
  max-width: 420px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-2xl);
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-5);
  border-bottom: 1px solid var(--border-color);
}

.modal-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--neutral-900);
  margin: 0;
}

.modal-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: var(--radius-lg);
  color: var(--neutral-400);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.modal-close:hover {
  background: var(--neutral-100);
  color: var(--neutral-700);
}

.close-icon {
  width: 18px;
  height: 18px;
}

.modal-body {
  padding: var(--space-5);
  font-size: var(--text-base);
  color: var(--neutral-700);
  line-height: var(--leading-relaxed);
  overflow-y: auto;
}

.modal-footer {
  display: flex;
  gap: var(--space-3);
  padding: var(--space-5);
  border-top: 1px solid var(--border-color);
  background: var(--neutral-50);
}

/* 梦境详情弹窗样式 */
.dream-detail-modal {
  max-width: 680px;
}

.dream-detail-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.detail-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.section-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--neutral-900);
  margin: 0;
  padding-bottom: var(--space-2);
  border-bottom: 1px solid var(--border-color);
}

.detail-meta {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.detail-date {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.detail-icon {
  width: 16px;
  height: 16px;
  color: var(--neutral-500);
  flex-shrink: 0;
}

.detail-label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--neutral-600);
}

.detail-value {
  font-size: var(--text-base);
  color: var(--neutral-900);
  font-weight: var(--font-medium);
}

.detail-content {
  font-size: var(--text-base);
  line-height: var(--leading-relaxed);
  color: var(--neutral-700);
  background: var(--neutral-50);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  white-space: pre-wrap;
}

.detail-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: var(--space-3);
}

.detail-stat {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3);
  background: var(--neutral-50);
  border-radius: var(--radius-lg);
}

.detail-actions {
  display: flex;
  gap: var(--space-3);
  width: 100%;
}

.detail-actions .spa-button-primary,
.detail-actions .spa-button-danger {
  flex: 1;
  justify-content: center;
}

/* 情绪和类型标签 */
.emotion-tags,
.type-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.emotion-tag,
.type-tag {
  display: inline-block;
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  color: white;
}

/* 关键词标签 */
.keyword-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.keyword-tag {
  display: flex;
  align-items: center;
  gap: var(--space-1_5);
  padding: var(--space-1_5) var(--space-2_5);
  background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  box-shadow: 0 2px 4px rgb(14 165 233 / 0.2);
  transition: all var(--transition-fast);
}

.keyword-tag:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgb(14 165 233 / 0.3);
}

.keyword-tag .keyword-text {
  color: white;
  font-weight: var(--font-semibold);
}

.keyword-tag .keyword-category {
  color: rgba(255, 255, 255, 0.9);
  font-size: var(--text-xs);
  padding: var(--space-0_5) var(--space-1_5);
  background: rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-full);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: var(--space-4);
    align-items: stretch;
    text-align: center;
  }

  .back-button {
    align-self: flex-start;
  }

  .dreams-grid {
    grid-template-columns: 1fr;
    gap: var(--space-4);
  }

  .dream-stats {
    gap: var(--space-3);
  }

  .search-input-wrapper {
    flex-direction: column;
    padding: var(--space-3);
  }

  .search-icon {
    display: none;
  }

  .search-button {
    width: 100%;
  }

  .dream-detail-modal {
    width: 95%;
  }

  .detail-stats {
    grid-template-columns: 1fr;
    gap: var(--space-2);
  }

  .detail-actions {
    flex-direction: column;
  }

  .detail-section {
    gap: var(--space-4);
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: var(--text-2xl);
  }

  .dream-card {
    padding: var(--space-4);
  }

  .dream-stats {
    flex-direction: column;
    gap: var(--space-2);
  }

  .pagination {
    flex-direction: column;
    gap: var(--space-3);
  }

  .modal-header,
  .modal-body,
  .modal-footer {
    padding: var(--space-4);
  }
}
</style>
