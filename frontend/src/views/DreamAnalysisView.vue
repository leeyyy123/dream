<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDreamsList, createAnalysis, getAnalysisList } from '../services/api'
import {
  ArrowLeft,
  Close,
  DataAnalysis,
  Calendar,
  Moon,
  Plus
} from '@element-plus/icons-vue'

const router = useRouter()

// 响应式数据
const analyses = ref([])
const loading = ref(false)
const error = ref('')
const showNewAnalysisModal = ref(false)
const showAnalysisDetailModal = ref(false)
const selectedAnalysis = ref(null)
const isCreating = ref(false)

// 新建分析表单
const analysisForm = ref({
  dateFrom: '',
  dateTo: ''
})

// 分析统计数据
const analysisData = ref({
  totalDreams: 0,
  avgSleepQuality: 0,
  avgLucidity: 0,
  mostCommonEmotions: [],
  mostCommonTypes: []
})

// 日期格式化
const formatDate = (dateString) => {
  if (!dateString) return '未知日期'

  const date = new Date(dateString)
  if (isNaN(date.getTime())) return '未知日期'

  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// 格式化日期时间
const formatDateTime = (dateString) => {
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return '未知时间'

  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
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
  return qualityMap[Math.round(quality)] || '未知'
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
  return lucidityMap[Math.round(lucidity)] || '未知'
}

// 设置日期范围（最近30天）
const setRecent30Days = () => {
  const endDate = new Date()
  const startDate = new Date()
  startDate.setDate(startDate.getDate() - 30)

  analysisForm.value.dateFrom = startDate.toISOString().split('T')[0]
  analysisForm.value.dateTo = endDate.toISOString().split('T')[0]
}

// 获取分析列表
const fetchAnalyses = async () => {
  loading.value = true
  error.value = ''

  try {
    const token = localStorage.getItem('authToken')
    if (!token) {
      router.push('/')
      return
    }

    const response = await getAnalysisList(token)

    if (response.Code === 200) {
      analyses.value = response.Data?.Analyses || []
    } else {
      error.value = response.Msg || '获取分析列表失败'
    }
  } catch (err) {
    console.error('获取分析列表失败:', err)
    error.value = '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 创建新分析
const createNewAnalysis = async () => {
  if (!analysisForm.value.dateFrom || !analysisForm.value.dateTo) {
    error.value = '请选择分析日期范围'
    return
  }

  isCreating.value = true
  error.value = ''

  try {
    const token = localStorage.getItem('authToken')
    const payload = {
      dateFrom: analysisForm.value.dateFrom,
      dateTo: analysisForm.value.dateTo
    }
    const response = await createAnalysis(payload, token)

    if (response.Code === 200) {
      showNewAnalysisModal.value = false
      analysisData.value = response.Data
      await fetchAnalyses()

      // 重置表单
      analysisForm.value = { dateFrom: '', dateTo: '' }
    } else {
      error.value = response.Msg || '创建分析失败'
    }
  } catch (err) {
    console.error('创建分析失败:', err)
    error.value = '网络错误，请稍后重试'
  } finally {
    isCreating.value = false
  }
}

// 查看分析详情
const viewAnalysisDetail = (analysis) => {
  selectedAnalysis.value = analysis
  showAnalysisDetailModal.value = true
}

// 关闭分析详情
const closeAnalysisDetail = () => {
  showAnalysisDetailModal.value = false
  selectedAnalysis.value = null
}

// 打开新建分析弹窗
const openNewAnalysisModal = () => {
  setRecent30Days()
  showNewAnalysisModal.value = true
  error.value = ''
}

// 关闭新建分析弹窗
const closeNewAnalysisModal = () => {
  showNewAnalysisModal.value = false
  analysisForm.value = { dateFrom: '', dateTo: '' }
  error.value = ''
}

// 返回主页
const goBack = () => {
  router.push('/main/home')
}

// 组件挂载
onMounted(() => {
  fetchAnalyses()
})
</script>

<template>
  <div class="analysis-container">
    <!-- 头部 -->
    <header class="header">
      <div class="container">
        <div class="header-content">
          <button class="back-button" @click="goBack">
            <component :is="ArrowLeft" class="back-icon" />
            <span>返回</span>
          </button>
          <h1 class="page-title">梦境分析</h1>
          <button class="spa-button-primary" @click="openNewAnalysisModal">
            <component :is="Plus" class="btn-icon" />
            <span>创建分析</span>
          </button>
        </div>
      </div>
    </header>

    <!-- 主要内容 -->
    <main class="main-content">
      <div class="container">
        <!-- 当前分析结果 -->
        <div v-if="analysisData.totalDreams > 0" class="analysis-summary">
          <h2 class="section-title">最新分析结果</h2>
          <div class="summary-grid">
            <div class="summary-card spa-card">
              <div class="summary-icon">
                <component :is="Moon" />
              </div>
              <div class="summary-content">
                <h3 class="summary-title">分析梦境数</h3>
                <p class="summary-value">{{ analysisData.totalDreams }} 个</p>
              </div>
            </div>

            <div class="summary-card spa-card">
              <div class="summary-icon">
                <component :is="DataAnalysis" />
              </div>
              <div class="summary-content">
                <h3 class="summary-title">平均睡眠质量</h3>
                <p class="summary-value">{{ getSleepQualityText(analysisData.avgSleepQuality) }}</p>
              </div>
            </div>

            <div class="summary-card spa-card">
              <div class="summary-icon">
                <component :is="DataAnalysis" />
              </div>
              <div class="summary-content">
                <h3 class="summary-title">平均梦境清晰度</h3>
                <p class="summary-value">{{ getLucidityText(analysisData.avgLucidity) }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-section">
          <div class="loading-spinner"></div>
          <span>加载分析列表...</span>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="error && analyses.length === 0" class="error-section">
          <p class="error-message">{{ error }}</p>
          <button class="spa-button-primary" @click="fetchAnalyses">重试</button>
        </div>

        <!-- 分析历史 -->
        <div v-if="analyses.length > 0" class="analyses-section">
          <h2 class="section-title">分析历史</h2>
          <div class="analyses-grid">
            <div
              v-for="analysis in analyses"
              :key="analysis.AnalysisID"
              class="analysis-card spa-card"
              @click="viewAnalysisDetail(analysis)"
            >
              <div class="analysis-header">
                <div class="analysis-icon">
                  <component :is="DataAnalysis" />
                </div>
                <div class="analysis-meta">
                  <h3 class="analysis-title">梦境分析报告</h3>
                  <p class="analysis-date">{{ formatDateTime(analysis.CreatedAt) }}</p>
                </div>
              </div>

              <div class="analysis-stats">
                <div class="analysis-stat">
                  <span class="stat-label">分析梦境</span>
                  <span class="stat-value">{{ analysis.DreamCount }} 个</span>
                </div>
                <div class="analysis-stat">
                  <span class="stat-label">时间范围</span>
                  <span class="stat-value">{{ formatDate(analysis.DateFrom) }} - {{ formatDate(analysis.DateTo) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else-if="!loading && !error" class="empty-state">
          <div class="empty-icon">
            <component :is="DataAnalysis" />
          </div>
          <h3 class="empty-title">还没有分析记录</h3>
          <p class="empty-description">创建你的第一个梦境分析报告</p>
          <button class="spa-button-primary" @click="openNewAnalysisModal">
            <component :is="Plus" class="btn-icon" />
            <span>创建分析</span>
          </button>
        </div>
      </div>
    </main>

    <!-- 创建分析弹窗 -->
    <div v-if="showNewAnalysisModal" class="modal-overlay" @click="closeNewAnalysisModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">创建梦境分析</h2>
          <button class="modal-close" @click="closeNewAnalysisModal">
            <component :is="Close" class="close-icon" />
          </button>
        </div>

        <div class="modal-body">
          <div v-if="error" class="form-error">
            {{ error }}
          </div>

          <div class="form-group">
            <label class="form-label">开始日期</label>
            <input
              v-model="analysisForm.dateFrom"
              type="date"
              class="form-input spa-input"
              :max="analysisForm.dateTo || new Date().toISOString().split('T')[0]"
            />
          </div>

          <div class="form-group">
            <label class="form-label">结束日期</label>
            <input
              v-model="analysisForm.dateTo"
              type="date"
              class="form-input spa-input"
              :min="analysisForm.dateFrom"
              :max="new Date().toISOString().split('T')[0]"
            />
          </div>
        </div>

        <div class="modal-footer">
          <button class="spa-button-secondary" @click="closeNewAnalysisModal" :disabled="isCreating">
            取消
          </button>
          <button
            class="spa-button-primary"
            @click="createNewAnalysis"
            :disabled="isCreating || !analysisForm.dateFrom || !analysisForm.dateTo"
          >
            {{ isCreating ? '分析中...' : '开始分析' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 分析详情弹窗 -->
    <div v-if="showAnalysisDetailModal" class="modal-overlay" @click="closeAnalysisDetail">
      <div class="modal modal-large" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">分析报告详情</h2>
          <button class="modal-close" @click="closeAnalysisDetail">
            <component :is="Close" class="close-icon" />
          </button>
        </div>

        <div class="modal-body">
          <div class="detail-content" v-html="selectedAnalysis?.AnalysisResult"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.analysis-container {
  min-height: 100vh;
  background: var(--neutral-50);
}

.container {
  max-width: 1200px;
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

/* 主内容区域 */
.main-content {
  padding: var(--space-8) 0;
}

.section-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  color: var(--neutral-900);
  margin: 0 0 var(--space-6) 0;
}

/* 分析摘要 */
.analysis-summary {
  margin-bottom: var(--space-12);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-5);
}

.summary-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-5);
  border: 1px solid var(--border-color);
}

.summary-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: var(--neutral-100);
  color: var(--neutral-700);
  border-radius: var(--radius-lg);
  flex-shrink: 0;
}

.summary-icon > * {
  width: 24px;
  height: 24px;
}

.summary-content {
  flex: 1;
}

.summary-title {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--neutral-600);
  margin: 0 0 var(--space-1) 0;
}

.summary-value {
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  color: var(--neutral-900);
  margin: 0;
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

/* 分析网格 */
.analyses-section {
  margin-bottom: var(--space-8);
}

.analyses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: var(--space-5);
}

.analysis-card {
  padding: var(--space-5);
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all var(--transition-base);
}

.analysis-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.analysis-header {
  display: flex;
  align-items: flex-start;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

.analysis-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: var(--neutral-100);
  color: var(--neutral-700);
  border-radius: var(--radius-lg);
  flex-shrink: 0;
}

.analysis-icon > * {
  width: 20px;
  height: 20px;
}

.analysis-meta {
  flex: 1;
}

.analysis-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--neutral-900);
  margin: 0 0 var(--space-1) 0;
}

.analysis-date {
  font-size: var(--text-sm);
  color: var(--neutral-500);
  margin: 0;
}

.analysis-stats {
  display: flex;
  gap: var(--space-6);
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-color);
}

.analysis-stat {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.stat-label {
  font-size: var(--text-xs);
  color: var(--neutral-600);
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

.modal {
  background: white;
  border-radius: var(--radius-2xl);
  max-width: 480px;
  width: 100%;
  box-shadow: var(--shadow-2xl);
  overflow: hidden;
}

.modal-large {
  max-width: 800px;
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
}

.form-group {
  margin-bottom: var(--space-5);
}

.form-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--neutral-700);
  margin-bottom: var(--space-2);
}

.form-input {
  width: 100%;
  padding: var(--space-2_5) var(--space-3);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  font-size: var(--text-base);
}

.form-input:focus {
  outline: none;
  border-color: var(--border-color-focus);
  box-shadow: 0 0 0 3px rgb(100 116 139 / 0.1);
}

.form-error {
  background: var(--error-50);
  color: var(--error-600);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  font-size: var(--text-sm);
  margin-bottom: var(--space-4);
}

.modal-footer {
  display: flex;
  gap: var(--space-3);
  padding: var(--space-5);
  border-top: 1px solid var(--border-color);
  background: var(--neutral-50);
}

.detail-content {
  line-height: var(--leading-relaxed);
  color: var(--neutral-700);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: var(--space-4);
    align-items: stretch;
    text-align: center;
  }

  .page-title {
    font-size: var(--text-xl);
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }

  .analyses-grid {
    grid-template-columns: 1fr;
    gap: var(--space-4);
  }

  .analysis-stats {
    flex-direction: column;
    gap: var(--space-3);
  }

  .modal-overlay {
    padding: var(--space-2);
  }

  .modal {
    max-width: 100%;
  }
}

@media (max-width: 480px) {
  .summary-card {
    padding: var(--space-4);
  }

  .analysis-card {
    padding: var(--space-4);
  }

  .section-title {
    font-size: var(--text-xl);
  }
}
</style>
