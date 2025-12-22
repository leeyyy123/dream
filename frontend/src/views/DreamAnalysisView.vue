<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDreamsList, createAnalysis, getAnalysisList } from '../services/api'

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
            ←
            <span>返回</span>
          </button>
          <h1 class="page-title">梦境分析</h1>
          <button class="btn-primary" @click="openNewAnalysisModal">
            创建分析
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
            <div class="summary-card">
              <div class="summary-icon">
                🧠
              </div>
              <div class="summary-content">
                <h3 class="summary-title">分析梦境数</h3>
                <p class="summary-value">{{ analysisData.totalDreams }} 个</p>
              </div>
            </div>

            <div class="summary-card">
              <div class="summary-icon">
                📅
              </div>
              <div class="summary-content">
                <h3 class="summary-title">平均睡眠质量</h3>
                <p class="summary-value">{{ getSleepQualityText(analysisData.avgSleepQuality) }}</p>
              </div>
            </div>

            <div class="summary-card">
              <div class="summary-icon">
                📅
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
          <button class="btn-primary" @click="fetchAnalyses">重试</button>
        </div>

        <!-- 分析历史 -->
        <div v-if="analyses.length > 0" class="analyses-section">
          <h2 class="section-title">分析历史</h2>
          <div class="analyses-grid">
            <div
              v-for="analysis in analyses"
              :key="analysis.AnalysisID"
              class="analysis-card"
              @click="viewAnalysisDetail(analysis)"
            >
              <div class="analysis-header">
                <div class="analysis-icon">
                  🧠
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
            🧠
          </div>
          <h3 class="empty-title">还没有分析记录</h3>
          <p class="empty-description">创建你的第一个梦境分析报告</p>
          <button class="btn-primary" @click="openNewAnalysisModal">
            创建分析
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
            ❌
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
              class="form-input"
              :max="analysisForm.dateTo || new Date().toISOString().split('T')[0]"
            />
          </div>

          <div class="form-group">
            <label class="form-label">结束日期</label>
            <input
              v-model="analysisForm.dateTo"
              type="date"
              class="form-input"
              :min="analysisForm.dateFrom"
              :max="new Date().toISOString().split('T')[0]"
            />
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="closeNewAnalysisModal" :disabled="isCreating">
            取消
          </button>
          <button
            class="btn-primary"
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
            ❌
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
  background: #f5f5f5;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 头部样式 */
.header {
  background: white;
  border-bottom: 1px solid #ddd;
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
  padding: 8px 16px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: #666;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.3s;
}

.back-button:hover {
  background: #f8f8f8;
  color: #333;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin: 0;
  flex: 1;
}

/* 主内容区域 */
.main-content {
  padding: 32px 0;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0 0 24px 0;
}

/* 分析摘要 */
.analysis-summary {
  margin-bottom: 48px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}

.summary-card {
  background: white;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.summary-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: #e8f4fd;
  color: #4299e1;
  border-radius: 12px;
  flex-shrink: 0;
  font-size: 24px;
}

.summary-content {
  flex: 1;
}

.summary-title {
  font-size: 16px;
  font-weight: 500;
  color: #666;
  margin: 0 0 4px 0;
}

.summary-value {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

/* 按钮基础样式 */
.btn-primary {
  background: #667eea;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
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

/* 分析网格 */
.analyses-section {
  margin-bottom: 32px;
}

.analyses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;
}

.analysis-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.analysis-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.analysis-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 16px;
}

.analysis-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: #e8f4fd;
  color: #4299e1;
  border-radius: 8px;
  flex-shrink: 0;
  font-size: 20px;
}

.analysis-meta {
  flex: 1;
}

.analysis-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 4px 0;
}

.analysis-date {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.analysis-stats {
  display: flex;
  gap: 24px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.analysis-stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.stat-value {
  font-size: 14px;
  color: #333;
  font-weight: 600;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 48px;
  color: #ccc;
  margin-bottom: 24px;
}

.empty-title {
  font-size: 20px;
  font-weight: 600;
  color: #666;
  margin: 0 0 8px 0;
}

.empty-description {
  font-size: 16px;
  color: #888;
  margin: 0 0 24px 0;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 16px;
}

.modal {
  background: white;
  border-radius: 12px;
  max-width: 500px;
  width: 100%;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
  overflow: hidden;
}

.modal-large {
  max-width: 800px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px;
  border-bottom: 1px solid #eee;
}

.modal-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
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
  border-radius: 6px;
  color: #999;
  cursor: pointer;
  transition: background 0.3s;
  font-size: 20px;
}

.modal-close:hover {
  background: #f8f8f8;
  color: #666;
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
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

.form-error {
  background: #fee;
  color: #e53e3e;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  margin-bottom: 16px;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 24px;
  border-top: 1px solid #eee;
  background: #f8f8f8;
}

.detail-content {
  line-height: 1.6;
  color: #444;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
    text-align: center;
  }

  .page-title {
    font-size: 24px;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }

  .analyses-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .analysis-stats {
    flex-direction: column;
    gap: 12px;
  }

  .modal-overlay {
    padding: 8px;
  }

  .modal {
    max-width: 100%;
  }
}

@media (max-width: 480px) {
  .summary-card {
    padding: 16px;
  }

  .analysis-card {
    padding: 16px;
  }

  .section-title {
    font-size: 20px;
  }
}
</style>