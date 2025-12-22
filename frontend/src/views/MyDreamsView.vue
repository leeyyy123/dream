<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDreamsList, deleteDream, getDreamDetail } from '../services/api'

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
      console.log('API响应:', response)
      console.log('response.Data:', response.Data)
      console.log('response.Data类型:', typeof response.Data)

      // 处理不同的数据结构
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
        console.warn('未识别的数据结构:', response)
      }

      totalCount.value = response.Count || response.TotalCount || dreams.value.length || 0
      console.log('梦境数据:', dreams.value)
      console.log('梦境数据长度:', dreams.value.length)
      console.log('总数:', totalCount.value)
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
      closeDreamDetail() // 关闭详情弹窗
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

// 显示梦境详情
const showDreamDetails = async (dream) => {
  try {
    const token = localStorage.getItem('authToken')
    if (!token) {
      router.push('/')
      return
    }

    // 获取完整的梦境详情
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
          <div class="header-left">
            <h1 class="page-title">我的梦境</h1>
            <p class="page-subtitle">共 {{ totalCount }} 个梦境记录</p>
          </div>
          <button class="btn-primary" @click="createNewDream">
            记录新梦境
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
              <input
                v-model="searchKeyword"
                type="text"
                placeholder="搜索梦境标题或内容..."
                class="form-input search-input"
                @keyup.enter="handleSearch"
              />
              <button class="btn-secondary search-button" @click="handleSearch">
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
          <button class="btn-primary" @click="fetchDreams">重试</button>
        </div>

        <!-- 梦境列表 -->
        <div v-else-if="dreams.length > 0" class="dreams-grid">
          <div
            v-for="dream in dreams"
            :key="dream.DreamID"
            class="dream-card clickable"
            @click="showDreamDetails(dream)"
          >
            <div class="dream-header">
              <div class="dream-icon">
                📖
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
            📖
          </div>
          <h3 class="empty-title">还没有梦境记录</h3>
          <p class="empty-description">开始记录你的第一个梦境吧</p>
          <button class="btn-primary" @click="createNewDream">
            记录梦境
          </button>
        </div>

        <!-- 分页 -->
        <div v-if="dreams.length > 0 && totalPages() > 1" class="pagination">
          <button
            :disabled="currentPage === 1"
            class="btn-secondary"
            @click="handlePageChange(currentPage - 1)"
          >
            上一页
          </button>

          <span class="page-info">
            第 {{ currentPage }} 页，共 {{ totalPages() }} 页
          </span>

          <button
            :disabled="currentPage === totalPages()"
            class="btn-secondary"
            @click="handlePageChange(currentPage + 1)"
          >
            下一页
          </button>
        </div>
      </div>
    </main>

    <!-- 删除确认弹窗 -->
    <div v-if="showDeleteConfirm" class="delete-modal-overlay" @click="cancelDelete">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">确认删除</h2>
          <button class="modal-close" @click="cancelDelete">
            ❌
          </button>
        </div>
        <div class="modal-body">
          <p>确定要删除梦境《{{ dreamToDelete?.Title }}》吗？此操作不可撤销。</p>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="cancelDelete">
            取消
          </button>
          <button class="btn-primary delete-button" @click="deleteDreamItem">
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
            ❌
          </button>
        </div>

        <div class="modal-body">
          <div class="dream-detail-content">
            <!-- 梦境基本信息 -->
            <div class="detail-section">
              <div class="detail-meta">
                <div class="detail-date">
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
            <button class="btn-primary edit-button" @click="editDream(selectedDream.DreamID)">
              ✏️ 编辑梦境
            </button>
            <button class="btn-secondary delete-button" @click="deleteFromDetail">
              🗑️ 删除梦境
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
  justify-content: space-between;
}

.header-left {
  flex: 1;
}

.page-title {
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--neutral-900);
  margin: 0 0 var(--space-2) 0;
  line-height: 1.2;
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
  max-width: 600px;
  margin: 0 auto;
}

.search-input-wrapper {
  display: flex;
  gap: var(--space-3);
}

.search-input {
  flex: 1;
  padding: var(--space-3) var(--space-4);
  background: white;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  font-size: var(--text-base);
  color: var(--neutral-900);
  transition: var(--transition-base);
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px rgb(59 130 246 / 0.1);
}

.search-input::placeholder {
  color: var(--neutral-400);
}

.search-button {
  flex-shrink: 0;
  padding: var(--space-3) var(--space-6);
  background: var(--primary-700);
  color: white;
  border: none;
  border-radius: var(--radius-lg);
  cursor: pointer;
  font-size: var(--text-sm);
  font-weight: 500;
  transition: var(--transition-base);
}

.search-button:hover {
  background: var(--primary-800);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

/* 按钮基础样式 */
.btn-primary {
  background: var(--primary-700);
  color: white;
  border: none;
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-lg);
  cursor: pointer;
  font-size: var(--text-sm);
  font-weight: 500;
  transition: var(--transition-base);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  text-decoration: none;
}

.btn-primary:hover {
  background: var(--primary-800);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-secondary {
  background: white;
  color: var(--neutral-700);
  border: 1px solid var(--border-color);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-lg);
  cursor: pointer;
  font-size: var(--text-sm);
  font-weight: 500;
  transition: var(--transition-base);
}

.btn-secondary:hover {
  background: var(--neutral-50);
  border-color: var(--border-color-hover);
  color: var(--neutral-800);
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 加载和错误状态 */
.loading-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: #666;
  font-size: 18px;
  gap: 16px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f0f0f0;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-section {
  text-align: center;
  padding: 80px 20px;
}

.error-message {
  color: #e53e3e;
  font-size: 18px;
  margin-bottom: 16px;
}

/* 梦境网格 */
.dreams-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: var(--space-6);
  margin-bottom: var(--space-8);
}

.dream-card {
  background: white;
  padding: var(--space-6);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  overflow: hidden;
  transition: var(--transition-base);
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
  border-color: var(--primary-300);
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
  background: var(--primary-50);
  color: var(--primary-600);
  border-radius: var(--radius-lg);
  flex-shrink: 0;
  font-size: 20px;
}

.dream-meta {
  flex: 1;
}

.dream-title {
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--neutral-900);
  margin: 0 0 var(--space-1) 0;
  line-height: 1.3;
}

.dream-date {
  font-size: var(--text-sm);
  color: var(--neutral-600);
  margin: 0;
}

.dream-actions {
  display: flex;
  gap: var(--space-2);
  flex-shrink: 0;
}

.action-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: var(--neutral-100);
  border: none;
  border-radius: var(--radius-lg);
  color: var(--neutral-600);
  cursor: pointer;
  transition: var(--transition-base);
  font-size: 16px;
}

.action-button:hover {
  background: var(--neutral-200);
  color: var(--neutral-900);
}

.delete-button:hover {
  background: var(--error-50);
  color: var(--error-600);
}

.dream-content {
  margin-bottom: var(--space-4);
}

.dream-text {
  font-size: var(--text-base);
  color: var(--neutral-700);
  line-height: 1.6;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.dream-stats {
  display: flex;
  gap: var(--space-6);
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
  color: var(--neutral-600);
  font-weight: 500;
}

.stat-value {
  font-size: var(--text-sm);
  color: var(--neutral-900);
  font-weight: 600;
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
  font-weight: 500;
}

/* 删除确认弹窗 */
.delete-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: var(--space-4);
}

/* 梦境详情弹窗和通用弹窗 */
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
  z-index: 1000;
  padding: var(--space-4);
}

.modal {
  background: white;
  border-radius: var(--radius-xl);
  max-width: 400px;
  width: 100%;
  box-shadow: var(--shadow-xl);
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-6);
  border-bottom: 1px solid var(--border-color);
}

.modal-title {
  font-size: var(--text-lg);
  font-weight: 600;
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
  color: var(--neutral-500);
  cursor: pointer;
  transition: var(--transition-base);
  font-size: 20px;
}

.modal-close:hover {
  background: var(--neutral-100);
  color: var(--neutral-700);
}

.modal-body {
  padding: var(--space-6);
  font-size: var(--text-base);
  color: var(--neutral-700);
  line-height: 1.5;
}

.modal-footer {
  display: flex;
  gap: var(--space-3);
  padding: var(--space-6);
  border-top: 1px solid var(--border-color);
  background: var(--neutral-50);
}

.modal-footer .btn-primary.delete-button {
  background: var(--error-600);
}

.modal-footer .btn-primary.delete-button:hover {
  background: var(--error-700);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: var(--space-4);
    align-items: stretch;
    text-align: center;
  }

  .dreams-grid {
    grid-template-columns: 1fr;
    gap: var(--space-4);
  }

  .dream-header {
    gap: var(--space-3);
  }

  .dream-stats {
    gap: var(--space-4);
  }

  .search-input-wrapper {
    flex-direction: column;
  }

  .search-button {
    width: 100%;
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
}

/* 梦境详情弹窗样式 */
.dream-detail-modal {
  max-width: 700px;
  width: 90%;
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
  font-size: var(--text-lg);
  font-weight: 600;
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
  gap: var(--space-3);
}

.detail-label {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--neutral-600);
  min-width: 100px;
}

.detail-value {
  font-size: var(--text-base);
  color: var(--neutral-900);
  font-weight: 500;
}

.detail-content {
  font-size: var(--text-base);
  line-height: 1.6;
  color: var(--neutral-700);
  background: var(--neutral-50);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  border-left: 4px solid var(--primary-500);
  white-space: pre-wrap;
}

.detail-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-4);
}

.detail-stat {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  background: var(--neutral-50);
  border-radius: var(--radius-lg);
}

.detail-actions {
  display: flex;
  gap: var(--space-3);
  width: 100%;
}

.detail-actions .btn-primary {
  flex: 1;
  justify-content: center;
  gap: var(--space-2);
}

.detail-actions .btn-secondary {
  flex: 1;
  justify-content: center;
  gap: var(--space-2);
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
  font-weight: 500;
  color: white;
  background: var(--primary-600);
}

/* 详情弹窗响应式设计 */
@media (max-width: 768px) {
  .dream-detail-modal {
    width: 95%;
    margin: var(--space-4);
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
</style>