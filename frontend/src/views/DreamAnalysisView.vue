<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { getDreamsList, createAnalysis, getAnalysisList } from '../services/api'
import * as echarts from 'echarts'
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
  mostCommonTypes: [],
  stats: null,
  aiAnalysis: ''
})

// 图表实例
const lineChartRef = ref(null)
const emotionPieChartRef = ref(null)
const typeBarChartRef = ref(null)
const wordCloudChartRef = ref(null)

// 详情弹窗中的图表实例
const detailLineChartRef = ref(null)
const detailEmotionPieChartRef = ref(null)
const detailTypeBarChartRef = ref(null)
const detailWordCloudChartRef = ref(null)

let lineChart = null
let emotionPieChart = null
let typeBarChart = null
let wordCloudChart = null
let detailLineChart = null
let detailEmotionPieChart = null
let detailTypeBarChart = null
let detailWordCloudChart = null

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

// 获取词云文字大小（基于出现次数）
const getKeywordSize = (count) => {
  const minSize = 12
  const maxSize = 32
  const maxCount = 10  // 假设最大出现次数为10
  const size = minSize + (count / maxCount) * (maxSize - minSize)
  return Math.min(Math.max(size, minSize), maxSize)
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
      StartDate: analysisForm.value.dateFrom,
      EndDate: analysisForm.value.dateTo
    }
    const response = await createAnalysis(payload, token)

    if (response.Code === 200) {
      showNewAnalysisModal.value = false

      // 处理分析结果
      const data = response.Data
      if (data && data.stats) {
        const stats = data.stats

        // 转换情绪数据格式（兼容新旧格式）
        let emotionsArray = []
        if (stats.emotionStats) {
          emotionsArray = Object.entries(stats.emotionStats)
            .sort((a, b) => {
              const countA = typeof a[1] === 'object' ? a[1].count : a[1]
              const countB = typeof b[1] === 'object' ? b[1].count : b[1]
              return countB - countA
            })
        }

        // 转换类型数据格式（兼容新旧格式）
        let typesArray = []
        if (stats.typeStats) {
          typesArray = Object.entries(stats.typeStats)
            .sort((a, b) => {
              const countA = typeof a[1] === 'object' ? a[1].count : a[1]
              const countB = typeof b[1] === 'object' ? b[1].count : b[1]
              return countB - countA
            })
        }

        analysisData.value = {
          totalDreams: stats.totalDreams || 0,
          avgSleepQuality: stats.sleepQualityStats ?
            Object.entries(stats.sleepQualityStats).reduce((sum, [quality, count]) => sum + quality * count, 0) /
            Object.values(stats.sleepQualityStats).reduce((sum, count) => sum + count, 0) : 3,
          avgLucidity: stats.lucidityStats ?
            Object.entries(stats.lucidityStats).reduce((sum, [lucidity, count]) => sum + lucidity * count, 0) /
            Object.values(stats.lucidityStats).reduce((sum, count) => sum + count, 0) : 3,
          mostCommonEmotions: emotionsArray,
          mostCommonTypes: typesArray,
          stats: stats,
          aiAnalysis: data.aiAnalysis || ''
        }
      }

      await fetchAnalyses()

      // 渲染图表
      await renderAllCharts()

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
const viewAnalysisDetail = async (analysis) => {
  selectedAnalysis.value = analysis
  showAnalysisDetailModal.value = true
  // 等待DOM更新后渲染图表
  await nextTick()
  renderDetailCharts()
}

// 关闭分析详情
const closeAnalysisDetail = () => {
  showAnalysisDetailModal.value = false
  selectedAnalysis.value = null
  // 清理图表
  if (detailLineChart) {
    detailLineChart.dispose()
    detailLineChart = null
  }
  if (detailEmotionPieChart) {
    detailEmotionPieChart.dispose()
    detailEmotionPieChart = null
  }
  if (detailTypeBarChart) {
    detailTypeBarChart.dispose()
    detailTypeBarChart = null
  }
  if (detailWordCloudChart) {
    detailWordCloudChart.dispose()
    detailWordCloudChart = null
  }
}

// 获取解析后的分析结果
const getParsedAnalysisResult = (analysis) => {
  if (!analysis) return ''

  // 如果有 Result 字段（JSON），解析并显示
  if (analysis.Result) {
    try {
      const resultData = typeof analysis.Result === 'string'
        ? JSON.parse(analysis.Result)
        : analysis.Result

      if (resultData.aiAnalysis) {
        return resultData.aiAnalysis
      }
    } catch (e) {
      console.error('解析分析结果失败:', e)
    }
  }

  // 否则使用 Recommendation 字段
  if (analysis.Recommendation) {
    return analysis.Recommendation
  }

  return '暂无分析报告'
}

// 获取解析后的统计数据
const getParsedStats = (analysis) => {
  if (!analysis || !analysis.Result) return null

  try {
    const resultData = typeof analysis.Result === 'string'
      ? JSON.parse(analysis.Result)
      : analysis.Result

    return resultData.stats || null
  } catch (e) {
    console.error('解析统计数据失败:', e)
    return null
  }
}

// 渲染折线图（梦境数量变化）
const renderLineChart = (container, dailyData) => {
  if (!container || !dailyData || dailyData.length === 0) return

  const chart = echarts.init(container)
  const dates = dailyData.map(d => d.date)
  const counts = dailyData.map(d => d.count)

  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>梦境数: {c}'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: 45,
        fontSize: 10
      }
    },
    yAxis: {
      type: 'value',
      name: '梦境数'
    },
    series: [{
      data: counts,
      type: 'line',
      smooth: true,
      lineStyle: {
        width: 3,
        color: '#667eea'
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(102, 126, 234, 0.5)' },
          { offset: 1, color: 'rgba(102, 126, 234, 0.1)' }
        ])
      },
      itemStyle: {
        color: '#667eea'
      }
    }]
  }

  chart.setOption(option)
  return chart
}

// 渲染情绪饼图
const renderEmotionPieChart = (container, emotionStats) => {
  if (!container || !emotionStats || Object.keys(emotionStats).length === 0) return

  const chart = echarts.init(container)
  const data = []
  const colors = []

  Object.entries(emotionStats).forEach(([name, value]) => {
    // 如果数据是对象（包含count和color），提取值
    const count = typeof value === 'object' ? value.count : value
    const color = typeof value === 'object' ? value.color : null
    data.push({ name, value: count })
    if (color) {
      colors.push(color)
    }
  })

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle',
      textStyle: {
        fontSize: 12
      }
    },
    series: [{
      name: '情绪分布',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['60%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 16,
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: data
    }]
  }

  // 使用从数据库获取的颜色
  if (colors.length > 0) {
    option.color = colors
  } else {
    // 如果没有颜色，使用默认颜色数组
    option.color = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#fee140', '#30cfd0']
  }

  chart.setOption(option)
  return chart
}

// 渲染类型柱状图
const renderTypeBarChart = (container, typeStats) => {
  if (!container || !typeStats || Object.keys(typeStats).length === 0) return

  const chart = echarts.init(container)
  const types = []
  const counts = []
  const colors = []

  Object.entries(typeStats).forEach(([type, data]) => {
    types.push(type)
    // 如果数据是对象（包含count和color），提取值
    const count = typeof data === 'object' ? data.count : data
    const color = typeof data === 'object' ? data.color : null
    counts.push(count)
    colors.push(color || '#667eea')
  })

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: types,
      axisLabel: {
        rotate: 45,
        fontSize: 10
      }
    },
    yAxis: {
      type: 'value',
      name: '出现次数'
    },
    series: [{
      data: counts.map((count, index) => ({
        value: count,
        itemStyle: {
          color: colors[index]
        }
      })),
      type: 'bar',
      barWidth: '60%'
    }]
  }

  chart.setOption(option)
  return chart
}

// 渲染词云（使用简单的标签云）
const renderWordCloud = (container, keywords) => {
  if (!container || !keywords || keywords.length === 0) return null

  // 不使用ECharts，直接返回null，由模板处理
  return null
}

// 渲染所有图表
const renderAllCharts = async () => {
  await nextTick()

  const stats = analysisData.value.stats
  if (!stats) return

  // 渲染折线图
  if (lineChartRef.value && stats.dailyDreamCounts) {
    if (lineChart) lineChart.dispose()
    lineChart = renderLineChart(lineChartRef.value, stats.dailyDreamCounts)
  }

  // 渲染情绪饼图
  if (emotionPieChartRef.value && stats.emotionStats) {
    if (emotionPieChart) emotionPieChart.dispose()
    emotionPieChart = renderEmotionPieChart(emotionPieChartRef.value, stats.emotionStats)
  }

  // 渲染类型柱状图
  if (typeBarChartRef.value && stats.typeStats) {
    if (typeBarChart) typeBarChart.dispose()
    typeBarChart = renderTypeBarChart(typeBarChartRef.value, stats.typeStats)
  }

  // 渲染词云
  if (wordCloudChartRef.value && stats.keywordStats?.topKeywords) {
    if (wordCloudChart) wordCloudChart.dispose()
    wordCloudChart = renderWordCloud(wordCloudChartRef.value, stats.keywordStats.topKeywords)
  }
}

// 渲染详情弹窗的所有图表
const renderDetailCharts = async () => {
  await nextTick()

  const stats = getParsedStats(selectedAnalysis.value)
  if (!stats) return

  // 渲染折线图
  if (detailLineChartRef.value && stats.dailyDreamCounts) {
    if (detailLineChart) detailLineChart.dispose()
    detailLineChart = renderLineChart(detailLineChartRef.value, stats.dailyDreamCounts)
  }

  // 渲染情绪饼图
  if (detailEmotionPieChartRef.value && stats.emotionStats) {
    if (detailEmotionPieChart) detailEmotionPieChart.dispose()
    detailEmotionPieChart = renderEmotionPieChart(detailEmotionPieChartRef.value, stats.emotionStats)
  }

  // 渲染类型柱状图
  if (detailTypeBarChartRef.value && stats.typeStats) {
    if (detailTypeBarChart) detailTypeBarChart.dispose()
    detailTypeBarChart = renderTypeBarChart(detailTypeBarChartRef.value, stats.typeStats)
  }

  // 渲染词云
  if (detailWordCloudChartRef.value && stats.keywordStats?.topKeywords) {
    if (detailWordCloudChart) detailWordCloudChart.dispose()
    detailWordCloudChart = renderWordCloud(detailWordCloudChartRef.value, stats.keywordStats.topKeywords)
  }
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

// 组件卸载时清理图表
onUnmounted(() => {
  if (lineChart) {
    lineChart.dispose()
    lineChart = null
  }
  if (emotionPieChart) {
    emotionPieChart.dispose()
    emotionPieChart = null
  }
  if (typeBarChart) {
    typeBarChart.dispose()
    typeBarChart = null
  }
  if (wordCloudChart) {
    wordCloudChart.dispose()
    wordCloudChart = null
  }
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

          <!-- 基本统计 -->
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

          <!-- 情绪分布 -->
          <div v-if="analysisData.mostCommonEmotions && analysisData.mostCommonEmotions.length > 0" class="analysis-detail-section">
            <h3 class="subsection-title">情绪分布（饼图）</h3>
            <div ref="emotionPieChartRef" class="chart-container chart-container-large"></div>
          </div>

          <!-- 梦境类型分布 -->
          <div v-if="analysisData.mostCommonTypes && analysisData.mostCommonTypes.length > 0" class="analysis-detail-section">
            <h3 class="subsection-title">梦境类型分布（柱状图）</h3>
            <div ref="typeBarChartRef" class="chart-container"></div>
          </div>

          <!-- 梦境数量变化 -->
          <div v-if="analysisData.stats && analysisData.stats.dailyDreamCounts && analysisData.stats.dailyDreamCounts.length > 0" class="analysis-detail-section">
            <h3 class="subsection-title">梦境数量变化（折线图）</h3>
            <div ref="lineChartRef" class="chart-container"></div>
          </div>

          <!-- 关键词词云 -->
          <div v-if="analysisData.stats && analysisData.stats.keywordStats && analysisData.stats.keywordStats.topKeywords && analysisData.stats.keywordStats.topKeywords.length > 0" class="analysis-detail-section">
            <h3 class="subsection-title">高频关键词</h3>
            <div class="simple-word-cloud">
              <span
                v-for="keyword in analysisData.stats.keywordStats.topKeywords"
                :key="keyword.text"
                class="word-tag"
                :style="{
                  fontSize: `${12 + (keyword.count * 2)}px`,
                  opacity: 0.6 + (keyword.count / 10) * 0.4
                }"
              >
                {{ keyword.text }}
              </span>
            </div>
          </div>

          <!-- AI分析报告 -->
          <div v-if="analysisData.aiAnalysis" class="analysis-detail-section">
            <h3 class="subsection-title">AI分析报告</h3>
            <div class="ai-report" v-html="analysisData.aiAnalysis.replace(/\n/g, '<br>')"></div>
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
      <div class="modal modal-large modal-scrollable" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">分析报告详情</h2>
          <button class="modal-close" @click="closeAnalysisDetail">
            <component :is="Close" class="close-icon" />
          </button>
        </div>

        <div class="modal-body">
          <!-- 基本信息 -->
          <div class="detail-meta-info">
            <div class="meta-info-item">
              <span class="meta-label">分析时间:</span>
              <span class="meta-value">{{ formatDateTime(selectedAnalysis.CreatedAt) }}</span>
            </div>
            <div class="meta-info-item">
              <span class="meta-label">时间范围:</span>
              <span class="meta-value">{{ formatDate(selectedAnalysis.DateFrom) }} - {{ formatDate(selectedAnalysis.DateTo) }}</span>
            </div>
            <div class="meta-info-item">
              <span class="meta-label">梦境数量:</span>
              <span class="meta-value">{{ selectedAnalysis.DreamCount }} 个</span>
            </div>
          </div>

          <!-- 图表展示 -->
          <div v-if="getParsedStats(selectedAnalysis)" class="detail-charts">
            <!-- 梦境数量变化 -->
            <div v-if="getParsedStats(selectedAnalysis).dailyDreamCounts && getParsedStats(selectedAnalysis).dailyDreamCounts.length > 0" class="detail-chart-section">
              <h4 class="detail-chart-title">梦境数量变化</h4>
              <div ref="detailLineChartRef" class="chart-container"></div>
            </div>

            <!-- 情绪分布 -->
            <div v-if="getParsedStats(selectedAnalysis).emotionStats && Object.keys(getParsedStats(selectedAnalysis).emotionStats).length > 0" class="detail-chart-section">
              <h4 class="detail-chart-title">情绪分布</h4>
              <div ref="detailEmotionPieChartRef" class="chart-container chart-container-large"></div>
            </div>

            <!-- 梦境类型分布 -->
            <div v-if="getParsedStats(selectedAnalysis).typeStats && Object.keys(getParsedStats(selectedAnalysis).typeStats).length > 0" class="detail-chart-section">
              <h4 class="detail-chart-title">梦境类型分布</h4>
              <div ref="detailTypeBarChartRef" class="chart-container"></div>
            </div>

            <!-- 关键词词云 -->
            <div v-if="getParsedStats(selectedAnalysis).keywordStats?.topKeywords && getParsedStats(selectedAnalysis).keywordStats.topKeywords.length > 0" class="detail-chart-section">
              <h4 class="detail-chart-title">高频关键词</h4>
              <div class="simple-word-cloud">
                <span
                  v-for="keyword in getParsedStats(selectedAnalysis).keywordStats.topKeywords"
                  :key="keyword.text"
                  class="word-tag"
                  :style="{
                    fontSize: `${12 + (keyword.count * 2)}px`,
                    opacity: 0.6 + (keyword.count / 10) * 0.4
                  }"
                >
                  {{ keyword.text }}
                </span>
              </div>
            </div>
          </div>

          <!-- AI分析报告 -->
          <div class="detail-report">
            <h3 class="detail-section-title">AI分析报告</h3>
            <div class="detail-content" v-html="getParsedAnalysisResult(selectedAnalysis).replace(/\n/g, '<br>')"></div>
          </div>
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

/* 可滚动弹窗 */
.modal-scrollable {
  max-height: 90vh;
  overflow-y: auto;
}

.modal-scrollable .modal-body {
  max-height: calc(90vh - 80px);
  overflow-y: auto;
}

/* 详情信息 */
.detail-meta-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding: var(--space-4);
  background: var(--neutral-50);
  border-radius: var(--radius-xl);
  margin-bottom: var(--space-5);
}

.meta-info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-2) 0;
  border-bottom: 1px solid var(--border-color);
}

.meta-info-item:last-child {
  border-bottom: none;
}

.meta-label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--neutral-600);
}

.meta-value {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--neutral-900);
}

.detail-report {
  margin-top: var(--space-4);
}

.detail-section-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--neutral-900);
  margin: 0 0 var(--space-4) 0;
  padding-bottom: var(--space-2);
  border-bottom: 2px solid var(--neutral-200);
}

/* 分析详细部分 */
.analysis-detail-section {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-2xl);
  padding: var(--space-6);
  margin-bottom: var(--space-6);
  box-shadow: var(--shadow-sm);
}

.subsection-title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--neutral-900);
  margin: 0 0 var(--space-5) 0;
}

/* 图表容器 */
.chart-container {
  width: 100%;
  height: 300px;
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.chart-container-large {
  height: 400px;
}

/* 详情弹窗图表 */
.detail-charts {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
  margin-bottom: var(--space-6);
}

.detail-chart-section {
  background: var(--neutral-50);
  border-radius: var(--radius-xl);
  padding: var(--space-5);
}

.detail-chart-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--neutral-900);
  margin: 0 0 var(--space-4) 0;
}

/* 旧的样式保留但不使用 */
.simple-word-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  padding: var(--space-4);
  background: var(--neutral-50);
  border-radius: var(--radius-xl);
  min-height: 200px;
  align-items: center;
  justify-content: center;
}

.word-tag {
  display: inline-block;
  padding: var(--space-1_5) var(--space-3);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: var(--radius-lg);
  font-weight: var(--font-semibold);
  transition: all var(--transition-fast);
  cursor: default;
  white-space: nowrap;
}

.word-tag:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 4px 12px rgb(102 126 234 / 0.3);
}

.emotion-distribution {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.emotion-bar-item {
  display: grid;
  grid-template-columns: 100px 1fr 50px;
  align-items: center;
  gap: var(--space-3);
}

.emotion-label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--neutral-700);
}

.emotion-bar {
  height: 24px;
  background: var(--neutral-100);
  border-radius: var(--radius-full);
  overflow: hidden;
  position: relative;
}

.emotion-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: var(--radius-full);
  transition: width 0.5s ease;
}

.emotion-count {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--neutral-900);
  text-align: right;
}

/* 类型分布 */
.type-distribution {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--space-3);
}

.type-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  background: var(--neutral-50);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  transition: all var(--transition-fast);
}

.type-item:hover {
  border-color: #667eea;
  background: rgb(102 126 234 / 0.05);
  transform: translateY(-1px);
}

.type-name {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--neutral-700);
}

.type-count {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--neutral-900);
}

/* 词云 */
.word-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
  padding: var(--space-4);
  background: var(--neutral-50);
  border-radius: var(--radius-xl);
  min-height: 200px;
  align-items: center;
  justify-content: center;
}

.word-cloud-item {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-2);
  color: var(--neutral-700);
  font-weight: var(--font-semibold);
  transition: all var(--transition-fast);
  cursor: default;
}

.word-cloud-item:hover {
  color: #667eea;
  transform: scale(1.1);
}

.word-category {
  font-size: 10px !important;
  font-weight: var(--font-normal) !important;
  color: var(--neutral-500);
  background: var(--neutral-200);
  padding: var(--space-0_5) var(--space-1);
  border-radius: var(--radius-full);
}

/* AI分析报告 */
.ai-report {
  line-height: var(--leading-relaxed);
  color: var(--neutral-700);
  font-size: var(--text-base);
  white-space: pre-wrap;
  padding: var(--space-4);
  background: var(--neutral-50);
  border-radius: var(--radius-xl);
  border-left: 4px solid #667eea;
}

.ai-report::v-deep p {
  margin-bottom: var(--space-3);
}

.ai-report::v-deep p:last-child {
  margin-bottom: 0;
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

  .emotion-bar-item {
    grid-template-columns: 80px 1fr 40px;
    gap: var(--space-2);
  }

  .type-distribution {
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

  .word-cloud {
    gap: var(--space-2);
  }

  .analysis-detail-section {
    padding: var(--space-4);
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
