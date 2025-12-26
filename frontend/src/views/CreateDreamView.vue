<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { createDream, getEmotions, getDreamTypes, getDreamDetail, updateDream, extractKeywords } from '../services/api'
import {
  ArrowLeft,
  Close,
  Star,
  Moon,
  MagicStick
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

// 判断是否为编辑模式
const isEditMode = computed(() => route.name === 'EditDream')
const dreamId = computed(() => route.params.id)

// 表单数据
const dreamForm = ref({
  title: '',
  content: '',
  dreamDate: '',
  sleepQuality: 3,
  lucidityLevel: 3,
  isPublic: false,
  selectedEmotions: [],
  selectedDreamTypes: [],
  selectedKeywords: []
})

// AI关键词相关状态
const aiKeywords = ref([])
const isLoadingKeywords = ref(false)
const keywordError = ref('')

// 表单验证错误
const formErrors = ref({
  title: '',
  content: '',
  dreamDate: ''
})

// 提交状态
const isSubmitting = ref(false)

// 情绪和梦境类型数据
const emotions = ref([])
const dreamTypes = ref([])
const isLoadingData = ref(true)

// 弹窗控制
const showEmotionModal = ref(false)
const showDreamTypeModal = ref(false)
const tempSelectedEmotions = ref([])
const tempSelectedDreamTypes = ref([])

// 睡眠质量星级配置
const sleepQualityConfig = {
  1: '很差',
  2: '较差',
  3: '一般',
  4: '较好',
  5: '很好'
}

// 梦境清晰度星级配置
const lucidityLevelConfig = {
  1: '非常模糊',
  2: '比较模糊',
  3: '一般',
  4: '比较清晰',
  5: '非常清晰'
}

// 星级评分临时值（用于悬停效果）
const sleepQualityHover = ref(0)
const lucidityLevelHover = ref(0)

// 验证表单
const validateForm = () => {
  formErrors.value = {
    title: '',
    content: '',
    dreamDate: ''
  }

  let isValid = true

  if (!dreamForm.value.title.trim()) {
    formErrors.value.title = '请输入梦境标题'
    isValid = false
  }

  if (!dreamForm.value.content.trim()) {
    formErrors.value.content = '请输入梦境内容'
    isValid = false
  } else if (dreamForm.value.content.trim().length < 10) {
    formErrors.value.content = '梦境内容至少需要10个字符'
    isValid = false
  }

  if (!dreamForm.value.dreamDate) {
    formErrors.value.dreamDate = '请选择梦境日期'
    isValid = false
  }

  return isValid
}

// 设置今天日期为默认值
const setTodayDate = () => {
  const today = new Date()
  dreamForm.value.dreamDate = today.toISOString().split('T')[0]
}

// 提交梦境（创建或更新）
const submitDream = async () => {
  if (!validateForm()) {
    return
  }

  isSubmitting.value = true

  try {
    const token = localStorage.getItem('authToken')
    if (!token) {
      alert('请先登录')
      router.push('/')
      return
    }

    const payload = {
      Title: dreamForm.value.title.trim(),
      Content: dreamForm.value.content.trim(),
      DreamDate: dreamForm.value.dreamDate,
      SleepQuality: dreamForm.value.sleepQuality,
      LucidityLevel: dreamForm.value.lucidityLevel,
      IsPublic: dreamForm.value.isPublic,
      EmotionIds: dreamForm.value.selectedEmotions,
      DreamTypeIds: dreamForm.value.selectedDreamTypes,
      Keywords: dreamForm.value.selectedKeywords
    }

    let response
    if (isEditMode.value) {
      response = await updateDream(dreamId.value, payload, token)
    } else {
      response = await createDream(payload, token)
    }

    if (response.Code === 200) {
      const action = isEditMode.value ? '更新' : '记录'
      alert(`梦境${action}成功！`)
      router.push('/main/my-dreams')
    } else {
      const action = isEditMode.value ? '更新' : '记录'
      alert(`${action}失败: ${response.Msg}`)
    }
  } catch (error) {
    console.error('提交梦境失败:', error)
    alert('网络错误，请稍后重试')
  } finally {
    isSubmitting.value = false
  }
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 设置睡眠质量评分
const setSleepQuality = (rating) => {
  dreamForm.value.sleepQuality = rating
}

// 设置梦境清晰度评分
const setLucidityLevel = (rating) => {
  dreamForm.value.lucidityLevel = rating
}

// 加载情绪和梦境类型数据
const loadEmotionsAndTypes = async () => {
  try {
    const token = localStorage.getItem('authToken')
    if (!token) {
      console.error('未找到登录令牌')
      router.push('/')
      return
    }

    const [emotionsResponse, dreamTypesResponse] = await Promise.all([
      getEmotions(token),
      getDreamTypes(token)
    ])

    if (emotionsResponse.Code === 200) {
      emotions.value = emotionsResponse.Data || []
    } else {
      console.error('获取情绪列表失败:', emotionsResponse.Msg)
    }

    if (dreamTypesResponse.Code === 200) {
      dreamTypes.value = dreamTypesResponse.Data || []
    } else {
      console.error('获取梦境类型列表失败:', dreamTypesResponse.Msg)
    }

  } catch (error) {
    console.error('加载情绪和梦境类型数据失败:', error)
  } finally {
    isLoadingData.value = false
  }
}

// 打开情绪选择弹窗
const openEmotionModal = () => {
  tempSelectedEmotions.value = [...dreamForm.value.selectedEmotions]
  showEmotionModal.value = true
}

// 关闭情绪选择弹窗
const closeEmotionModal = () => {
  showEmotionModal.value = false
  tempSelectedEmotions.value = []
}

// 确认情绪选择
const confirmEmotionSelection = () => {
  dreamForm.value.selectedEmotions = [...tempSelectedEmotions.value]
  closeEmotionModal()
}

// 在弹窗中切换情绪选择
const toggleTempEmotion = (emotionId) => {
  const index = tempSelectedEmotions.value.indexOf(emotionId)
  if (index > -1) {
    tempSelectedEmotions.value.splice(index, 1)
  } else {
    tempSelectedEmotions.value.push(emotionId)
  }
}

// 打开梦境类型选择弹窗
const openDreamTypeModal = () => {
  tempSelectedDreamTypes.value = [...dreamForm.value.selectedDreamTypes]
  showDreamTypeModal.value = true
}

// 关闭梦境类型选择弹窗
const closeDreamTypeModal = () => {
  showDreamTypeModal.value = false
  tempSelectedDreamTypes.value = []
}

// 确认梦境类型选择
const confirmDreamTypeSelection = () => {
  dreamForm.value.selectedDreamTypes = [...tempSelectedDreamTypes.value]
  closeDreamTypeModal()
}

// 在弹窗中切换梦境类型选择
const toggleTempDreamType = (typeId) => {
  const index = tempSelectedDreamTypes.value.indexOf(typeId)
  if (index > -1) {
    tempSelectedDreamTypes.value.splice(index, 1)
  } else {
    tempSelectedDreamTypes.value.push(typeId)
  }
}

// 删除已选择的情绪
const removeSelectedEmotion = (emotionId) => {
  const index = dreamForm.value.selectedEmotions.indexOf(emotionId)
  if (index > -1) {
    dreamForm.value.selectedEmotions.splice(index, 1)
  }
}

// 删除已选择的梦境类型
const removeSelectedDreamType = (typeId) => {
  const index = dreamForm.value.selectedDreamTypes.indexOf(typeId)
  if (index > -1) {
    dreamForm.value.selectedDreamTypes.splice(index, 1)
  }
}

// 获取已选择的情绪对象
const getSelectedEmotionObjects = () => {
  return emotions.value
    .filter(emotion => dreamForm.value.selectedEmotions.includes(emotion.EmotionID))
}

// 获取已选择的梦境类型对象
const getSelectedDreamTypeObjects = () => {
  return dreamTypes.value
    .filter(type => dreamForm.value.selectedDreamTypes.includes(type.TypeID))
}

// 提取AI关键词
const fetchAIKeywords = async () => {
  const content = dreamForm.value.content.trim()
  if (!content || content.length < 10) {
    keywordError.value = '请先输入梦境内容（至少10字）'
    return
  }

  isLoadingKeywords.value = true
  keywordError.value = ''

  try {
    const token = localStorage.getItem('authToken')
    if (!token) {
      keywordError.value = '请先登录'
      return
    }

    const response = await extractKeywords(content, token)

    if (response.Code === 200 && response.Data) {
      // AI返回的关键词格式: { keywords: [{text: "...", category: "...", weight: N}, ...] }
      const keywords = response.Data.keywords || []

      // 取最多5个关键词
      aiKeywords.value = keywords.slice(0, 5).map(kw => ({
        text: kw.text || '',
        category: kw.category || 'other',
        weight: kw.weight || 2
      }))
    } else {
      keywordError.value = response.Msg || '关键词提取失败'
    }
  } catch (error) {
    console.error('提取关键词失败:', error)
    keywordError.value = '网络错误，请稍后重试'
  } finally {
    isLoadingKeywords.value = false
  }
}

// 切换关键词选择
const toggleKeyword = (keyword) => {
  const index = dreamForm.value.selectedKeywords.findIndex(
    kw => kw.text === keyword.text
  )
  if (index > -1) {
    dreamForm.value.selectedKeywords.splice(index, 1)
  } else {
    dreamForm.value.selectedKeywords.push(keyword)
  }
}

// 检查关键词是否已选择
const isKeywordSelected = (keyword) => {
  return dreamForm.value.selectedKeywords.some(
    kw => kw.text === keyword.text
  )
}

// 删除已选择的关键词
const removeSelectedKeyword = (keyword) => {
  const index = dreamForm.value.selectedKeywords.findIndex(
    kw => kw.text === keyword.text
  )
  if (index > -1) {
    dreamForm.value.selectedKeywords.splice(index, 1)
  }
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

// 加载梦境详情（编辑模式）
const loadDreamDetail = async () => {
  if (!isEditMode.value) return

  try {
    const token = localStorage.getItem('authToken')
    if (!token) {
      router.push('/')
      return
    }

    const response = await getDreamDetail(dreamId.value, token)
    if (response.Code === 200 && response.Data) {
      const data = response.Data
      dreamForm.value = {
        title: data.Title || '',
        content: data.Content || '',
        dreamDate: formatDateForInput(data.DreamDate),
        sleepQuality: data.SleepQuality || 3,
        lucidityLevel: data.LucidityLevel || 3,
        isPublic: data.IsPublic || false,
        selectedEmotions: data.Emotions?.map(e => e.EmotionID) || [],
        selectedDreamTypes: data.DreamTypes?.map(t => t.TypeID) || [],
        selectedKeywords: data.Keywords?.map(k => ({
          text: k.KeywordText,
          category: k.Category,
          weight: k.Weight || 2
        })) || []
      }
    } else {
      alert(`获取梦境详情失败: ${response.Msg}`)
      router.push('/main/my-dreams')
    }
  } catch (error) {
    console.error('获取梦境详情失败:', error)
    alert('获取梦境详情失败，请稍后重试')
    router.push('/main/my-dreams')
  }
}

// 格式化日期为YYYY-MM-DD
const formatDateForInput = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toISOString().split('T')[0]
}

// 组件挂载时设置默认日期和加载数据
onMounted(() => {
  if (isEditMode.value) {
    loadDreamDetail()
    loadEmotionsAndTypes()
  } else {
    setTodayDate()
    loadEmotionsAndTypes()
  }
})
</script>

<template>
  <div class="create-dream-container">
    <!-- 头部 -->
    <header class="header">
      <div class="container">
        <div class="header-content">
          <button class="back-button" @click="goBack">
            <component :is="ArrowLeft" class="back-icon" />
            <span>返回</span>
          </button>
          <h1 class="page-title">{{ isEditMode ? '编辑梦境' : '记录梦境' }}</h1>
          <div class="header-spacer"></div>
        </div>
      </div>
    </header>

    <!-- 主要内容 -->
    <main class="main-content">
      <div class="container">
        <!-- 编辑模式提示 -->
        <div v-if="isEditMode && !isLoadingData" class="edit-notice">
          <component :is="Moon" class="notice-icon" />
          <span>你正在编辑梦境记录</span>
        </div>

        <div class="form-card">
          <!-- 梦境标题 -->
          <div class="form-section">
            <div class="form-group">
              <label class="form-label">梦境标题 <span class="required">*</span></label>
              <input
                v-model="dreamForm.title"
                type="text"
                class="form-input spa-input"
                :class="{ 'input-error': formErrors.title }"
                placeholder="给你的梦境起个标题..."
                maxlength="100"
              />
              <div v-if="formErrors.title" class="error-message">
                {{ formErrors.title }}
              </div>
            </div>

            <!-- 梦境日期 -->
            <div class="form-group">
              <label class="form-label">梦境日期 <span class="required">*</span></label>
              <input
                v-model="dreamForm.dreamDate"
                type="date"
                class="form-input spa-input"
                :class="{ 'input-error': formErrors.dreamDate }"
                :max="new Date().toISOString().split('T')[0]"
              />
              <div v-if="formErrors.dreamDate" class="error-message">
                {{ formErrors.dreamDate }}
              </div>
            </div>
          </div>

          <!-- 梦境内容 -->
          <div class="form-section">
            <div class="form-group">
              <label class="form-label">梦境内容 <span class="required">*</span></label>
              <textarea
                v-model="dreamForm.content"
                class="form-input spa-input spa-textarea"
                :class="{ 'input-error': formErrors.content }"
                placeholder="详细描述你的梦境（不少于10字）..."
                rows="8"
                maxlength="2000"
              ></textarea>
              <div class="char-count">
                {{ dreamForm.content.length }}/2000
              </div>
              <div v-if="formErrors.content" class="error-message">
                {{ formErrors.content }}
              </div>
            </div>

            <!-- AI关键词提取 -->
            <div class="keyword-section">
              <div class="keyword-header">
                <label class="form-label">AI关键词提取</label>
                <button
                  class="extract-keywords-btn"
                  @click="fetchAIKeywords"
                  :disabled="isLoadingKeywords || !dreamForm.content || dreamForm.content.length < 10"
                >
                  <component :is="MagicStick" class="btn-icon" />
                  <span>{{ isLoadingKeywords ? '提取中...' : '获取关键词' }}</span>
                </button>
              </div>

              <!-- 错误提示 -->
              <div v-if="keywordError" class="keyword-error">
                {{ keywordError }}
              </div>

              <!-- AI提取的关键词 -->
              <div v-if="aiKeywords.length > 0" class="ai-keywords-container">
                <div class="keywords-label">
                  点击选择至少一个关键词（共{{ aiKeywords.length }}个）
                </div>
                <div class="keywords-grid">
                  <div
                    v-for="(keyword, index) in aiKeywords"
                    :key="index"
                    class="keyword-item"
                    :class="{ selected: isKeywordSelected(keyword) }"
                    @click="toggleKeyword(keyword)"
                  >
                    <span class="keyword-text">{{ keyword.text }}</span>
                    <span class="keyword-category">{{ getCategoryName(keyword.category) }}</span>
                  </div>
                </div>
              </div>

              <!-- 已选择的关键词 -->
              <div v-if="dreamForm.selectedKeywords.length > 0" class="selected-keywords-container">
                <div class="selected-keywords-label">
                  已选择 {{ dreamForm.selectedKeywords.length }} 个关键词
                </div>
                <div class="selected-keywords-list">
                  <div
                    v-for="(keyword, index) in dreamForm.selectedKeywords"
                    :key="index"
                    class="selected-keyword-tag"
                  >
                    <span class="tag-text">{{ keyword.text }}</span>
                    <button class="tag-remove" @click="removeSelectedKeyword(keyword)">
                      <component :is="Close" class="remove-icon" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 情绪和梦境类型选择 -->
          <div v-if="isLoadingData" class="loading-section">
            <div class="loading-spinner"></div>
            <span>加载数据中...</span>
          </div>

          <div v-else class="form-section">
            <!-- 情绪选择 -->
            <div class="form-group">
              <label class="form-label">情绪选择</label>
              <button class="selection-trigger" @click="openEmotionModal">
                <span>选择情绪</span>
              </button>

              <div v-if="dreamForm.selectedEmotions.length > 0" class="selected-items">
                <div class="selected-items-label">
                  已选择 {{ dreamForm.selectedEmotions.length }} 种情绪
                </div>
                <div class="tags-grid">
                  <div
                    v-for="emotion in getSelectedEmotionObjects()"
                    :key="emotion.EmotionID"
                    class="tag"
                  >
                    <div class="tag-color" :style="{ backgroundColor: emotion.Color }"></div>
                    <span class="tag-text">{{ emotion.EmotionName }}</span>
                    <button class="tag-remove" @click="removeSelectedEmotion(emotion.EmotionID)">
                      <component :is="Close" class="remove-icon" />
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 梦境类型选择 -->
            <div class="form-group">
              <label class="form-label">梦境类型</label>
              <button class="selection-trigger" @click="openDreamTypeModal">
                <span>选择梦境类型</span>
              </button>

              <div v-if="dreamForm.selectedDreamTypes.length > 0" class="selected-items">
                <div class="selected-items-label">
                  已选择 {{ dreamForm.selectedDreamTypes.length }} 种类型
                </div>
                <div class="tags-grid">
                  <div
                    v-for="dreamType in getSelectedDreamTypeObjects()"
                    :key="dreamType.TypeID"
                    class="tag"
                  >
                    <div class="tag-color" :style="{ backgroundColor: dreamType.Color }"></div>
                    <span class="tag-text">{{ dreamType.TypeName }}</span>
                    <button class="tag-remove" @click="removeSelectedDreamType(dreamType.TypeID)">
                      <component :is="Close" class="remove-icon" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 评估选项 -->
          <div class="form-section">
            <!-- 睡眠质量 -->
            <div class="form-group">
              <label class="form-label">睡眠质量</label>
              <div class="rating-container">
                <div class="stars">
                  <span
                    v-for="star in 5"
                    :key="star"
                    :class="['star-icon', {
                      'active': star <= dreamForm.sleepQuality
                    }]"
                    @click="setSleepQuality(star)"
                  >
                    <component :is="Star" class="star" />
                  </span>
                </div>
                <span class="rating-label">
                  {{ sleepQualityConfig[dreamForm.sleepQuality] }}
                </span>
              </div>
            </div>

            <!-- 梦境清晰度 -->
            <div class="form-group">
              <label class="form-label">梦境清晰度</label>
              <div class="rating-container">
                <div class="stars">
                  <span
                    v-for="star in 5"
                    :key="star"
                    :class="['star-icon', {
                      'active': star <= dreamForm.lucidityLevel
                    }]"
                    @click="setLucidityLevel(star)"
                  >
                    <component :is="Star" class="star" />
                  </span>
                </div>
                <span class="rating-label">
                  {{ lucidityLevelConfig[dreamForm.lucidityLevel] }}
                </span>
              </div>
            </div>

            <!-- 隐私设置 -->
            <div class="form-group">
              <label class="form-label">隐私设置</label>
              <div class="privacy-toggle">
                <label class="toggle">
                  <input
                    v-model="dreamForm.isPublic"
                    type="checkbox"
                    class="toggle-input"
                  />
                  <span class="toggle-slider"></span>
                  <span class="toggle-status">{{ dreamForm.isPublic ? '公开' : '私密' }}</span>
                </label>
                <p class="privacy-description">
                  {{ dreamForm.isPublic ? '管理员可以看到这个梦境' : '只有你能看到这个梦境' }}
                </p>
              </div>
            </div>
          </div>

          <!-- 提交按钮 -->
          <div class="form-actions">
            <button
              class="spa-button-primary submit-button"
              @click="submitDream"
              :disabled="isSubmitting"
            >
              {{ isSubmitting ? (isEditMode ? '更新中...' : '记录中...') : (isEditMode ? '更新梦境' : '记录梦境') }}
            </button>
          </div>
        </div>
      </div>
    </main>

    <!-- 情绪选择弹窗 -->
    <div v-if="showEmotionModal" class="modal-overlay" @click="closeEmotionModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">选择情绪</h2>
          <button class="modal-close" @click="closeEmotionModal">
            <component :is="Close" class="close-icon" />
          </button>
        </div>
        <div class="modal-body">
          <div class="selection-grid">
            <div
              v-for="emotion in emotions"
              :key="emotion.EmotionID"
              class="selection-item"
              :class="{ selected: tempSelectedEmotions.includes(emotion.EmotionID) }"
              @click="toggleTempEmotion(emotion.EmotionID)"
            >
              <div class="item-color" :style="{ backgroundColor: emotion.Color }"></div>
              <span class="item-name">{{ emotion.EmotionName }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <span class="selection-count">
            已选择 {{ tempSelectedEmotions.length }} 种情绪
          </span>
          <div class="modal-actions">
            <button class="spa-button-secondary" @click="closeEmotionModal">取消</button>
            <button class="spa-button-primary" @click="confirmEmotionSelection">确定</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 梦境类型选择弹窗 -->
    <div v-if="showDreamTypeModal" class="modal-overlay" @click="closeDreamTypeModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">选择梦境类型</h2>
          <button class="modal-close" @click="closeDreamTypeModal">
            <component :is="Close" class="close-icon" />
          </button>
        </div>
        <div class="modal-body">
          <div class="selection-grid">
            <div
              v-for="dreamType in dreamTypes"
              :key="dreamType.TypeID"
              class="selection-item"
              :class="{ selected: tempSelectedDreamTypes.includes(dreamType.TypeID) }"
              @click="toggleTempDreamType(dreamType.TypeID)"
            >
              <div class="item-color" :style="{ backgroundColor: dreamType.Color }"></div>
              <span class="item-name">{{ dreamType.TypeName }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <span class="selection-count">
            已选择 {{ tempSelectedDreamTypes.length }} 种类型
          </span>
          <div class="modal-actions">
            <button class="spa-button-secondary" @click="closeDreamTypeModal">取消</button>
            <button class="spa-button-primary" @click="confirmDreamTypeSelection">确定</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 基础样式 */
.create-dream-container {
  min-height: 100vh;
  background: var(--neutral-50);
}

/* 编辑模式提示 */
.edit-notice {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  background: var(--neutral-100);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--space-3);
  margin-bottom: var(--space-5);
  font-size: var(--text-sm);
  color: var(--neutral-700);
}

.notice-icon {
  width: 18px;
  height: 18px;
}

/* 头部样式 */
.header {
  background: white;
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
}

.header-content {
  display: flex;
  align-items: center;
  height: 64px;
  gap: var(--space-4);
}

.back-button {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
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
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--neutral-900);
  margin: 0;
  flex: 1;
}

.header-spacer {
  width: 70px;
}

/* 主内容区域 */
.main-content {
  padding: var(--space-8) 0;
}

.form-card {
  background: white;
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  padding: var(--space-8);
  max-width: 760px;
  margin: 0 auto;
}

.form-section {
  margin-bottom: var(--space-8);
}

.form-section:last-child {
  margin-bottom: 0;
}

.form-group {
  margin-bottom: var(--space-5);
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--neutral-900);
  margin-bottom: var(--space-2);
}

.required {
  color: var(--error-500);
}

/* 关键词部分样式 */
.keyword-section {
  margin-top: var(--space-6);
  padding: var(--space-5);
  background: var(--neutral-50);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
}

.keyword-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.extract-keywords-btn {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
  color: white;
  border: none;
  border-radius: var(--radius-lg);
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: 0 2px 8px rgb(14 165 233 / 0.3);
}

.extract-keywords-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgb(14 165 233 / 0.4);
}

.extract-keywords-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-icon {
  width: 16px;
  height: 16px;
}

.keyword-error {
  color: var(--error-600);
  font-size: var(--text-sm);
  padding: var(--space-2) var(--space-3);
  background: var(--error-50);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-3);
}

.ai-keywords-container {
  margin-top: var(--space-4);
}

.keywords-label {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--neutral-700);
  margin-bottom: var(--space-3);
}

.keywords-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: var(--space-2);
}

.keyword-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-3);
  background: white;
  border: 2px solid var(--border-color);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.keyword-item:hover {
  border-color: #0ea5e9;
  background: rgb(14 165 233 / 0.05);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgb(0 0 0 / 0.1);
}

.keyword-item.selected {
  border-color: #0ea5e9;
  background: linear-gradient(135deg, rgb(14 165 233 / 0.1) 0%, rgb(6 182 212 / 0.1) 100%);
  box-shadow: 0 0 0 2px rgb(14 165 233 / 0.2);
}

.keyword-text {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--neutral-900);
}

.keyword-category {
  font-size: var(--text-xs);
  color: var(--neutral-500);
  padding: var(--space-0_5) var(--space-2);
  background: var(--neutral-100);
  border-radius: var(--radius-full);
}

.selected-keywords-container {
  margin-top: var(--space-4);
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-color);
}

.selected-keywords-label {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--neutral-700);
  margin-bottom: var(--space-3);
}

.selected-keywords-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.selected-keyword-tag {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-1_5) var(--space-2_5);
  background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
  color: white;
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
}

.selected-keyword-tag .tag-text {
  color: white;
}

.selected-keyword-tag .tag-remove {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-0_5);
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: var(--radius-full);
  color: white;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.selected-keyword-tag .tag-remove:hover {
  background: rgba(255, 255, 255, 0.3);
}

.selected-keyword-tag .remove-icon {
  width: 12px;
  height: 12px;
}

.form-input {
  width: 100%;
  padding: var(--space-2_5) var(--space-3);
  background: white;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  font-size: var(--text-base);
  color: var(--neutral-900);
  transition: all var(--transition-fast);
}

.form-input:focus {
  outline: none;
  border-color: var(--border-color-focus);
  box-shadow: 0 0 0 3px rgb(100 116 139 / 0.1);
}

.spa-textarea {
  resize: vertical;
  min-height: 180px;
  font-family: inherit;
  line-height: var(--leading-relaxed);
}

.form-input::placeholder {
  color: var(--neutral-400);
}

.input-error {
  border-color: var(--error-500) !important;
  box-shadow: 0 0 0 3px rgb(220 38 38 / 0.1) !important;
}

.char-count {
  text-align: right;
  font-size: var(--text-sm);
  color: var(--neutral-500);
  margin-top: var(--space-2);
}

.error-message {
  color: var(--error-600);
  font-size: var(--text-sm);
  margin-top: var(--space-2);
  font-weight: var(--font-medium);
}

.selection-trigger {
  width: 100%;
  padding: var(--space-2_5) var(--space-3);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  background: white;
  color: var(--neutral-900);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: all var(--transition-fast);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
}

.selection-trigger:hover {
  border-color: var(--border-color-hover);
  background: var(--neutral-50);
}

/* 已选择项目 */
.selected-items {
  margin-top: var(--space-4);
}

.selected-items-label {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--neutral-900);
  margin-bottom: var(--space-3);
}

.tags-grid {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.tag {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-1_5) var(--space-2_5);
  background: white;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  color: var(--neutral-700);
  transition: all var(--transition-fast);
}

.tag:hover {
  background: var(--neutral-50);
  box-shadow: var(--shadow-sm);
}

.tag-color {
  width: 10px;
  height: 10px;
  border-radius: var(--radius-full);
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 1px 2px rgb(0 0 0 / 0.1);
}

.tag-text {
  font-weight: var(--font-medium);
}

.tag-remove {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-0_5);
  background: transparent;
  border: none;
  border-radius: var(--radius-full);
  color: var(--neutral-400);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.tag-remove:hover {
  background: var(--error-50);
  color: var(--error-600);
}

.remove-icon {
  width: 14px;
  height: 14px;
}

/* 评分组件 */
.rating-container {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-3);
  background: var(--neutral-50);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
}

.stars {
  display: flex;
  gap: var(--space-1);
}

.star-icon {
  color: var(--neutral-300);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.star {
  width: 22px;
  height: 22px;
}

.star-icon.active {
  color: var(--warning-500);
}

.rating-label {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--neutral-900);
  min-width: 50px;
}

/* 隐私设置 */
.privacy-toggle {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.toggle {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  cursor: pointer;
}

.toggle-input {
  display: none;
}

.toggle-slider {
  position: relative;
  width: 40px;
  height: 22px;
  background: var(--neutral-300);
  border-radius: var(--radius-full);
  transition: all var(--transition-fast);
}

.toggle-slider::before {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 18px;
  height: 18px;
  background: white;
  border-radius: var(--radius-full);
  transition: all var(--transition-fast);
  box-shadow: 0 2px 4px rgb(0 0 0 / 0.2);
}

.toggle-input:checked + .toggle-slider {
  background: var(--neutral-900);
}

.toggle-input:checked + .toggle-slider::before {
  transform: translateX(18px);
}

.toggle-status {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--neutral-900);
}

.privacy-description {
  font-size: var(--text-sm);
  color: var(--neutral-500);
  margin: 0;
  padding-left: 63px;
}

/* 提交按钮 */
.form-actions {
  display: flex;
  justify-content: center;
  padding-top: var(--space-8);
  border-top: 1px solid var(--border-color);
}

.submit-button {
  min-width: 180px;
  padding: var(--space-3) var(--space-8);
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
}

/* 加载状态 */
.loading-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
  padding: var(--space-8);
  color: var(--neutral-500);
  font-size: var(--text-base);
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid var(--neutral-200);
  border-top: 2px solid var(--neutral-900);
  border-radius: var(--radius-full);
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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
  max-width: 560px;
  width: 100%;
  max-height: 80vh;
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
  flex: 1;
  padding: var(--space-5);
  overflow-y: auto;
}

.selection-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: var(--space-2);
}

.selection-item {
  display: flex;
  align-items: center;
  gap: var(--space-2_5);
  padding: var(--space-2_5) var(--space-3);
  background: white;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.selection-item:hover {
  border-color: var(--neutral-400);
  background: var(--neutral-50);
}

.selection-item.selected {
  border-color: var(--neutral-900);
  background: var(--neutral-50);
  box-shadow: 0 0 0 1px var(--neutral-900);
}

.item-color {
  width: 14px;
  height: 14px;
  border-radius: var(--radius-full);
  border: 2px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 1px 3px rgb(0 0 0 / 0.2);
  flex-shrink: 0;
}

.item-name {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--neutral-700);
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-5);
  border-top: 1px solid var(--border-color);
  background: var(--neutral-50);
}

.selection-count {
  font-size: var(--text-sm);
  color: var(--neutral-600);
  font-weight: var(--font-medium);
}

.modal-actions {
  display: flex;
  gap: var(--space-2);
}

/* 容器样式 */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-6);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    height: 60px;
    padding: 0 var(--space-4);
  }

  .page-title {
    font-size: var(--text-lg);
  }

  .main-content {
    padding: var(--space-6) 0;
  }

  .form-card {
    padding: var(--space-5);
    border-radius: var(--radius-xl);
  }

  .selection-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: var(--space-2);
  }

  .modal-header,
  .modal-body,
  .modal-footer {
    padding: var(--space-4);
  }

  .modal-footer {
    flex-direction: column;
    gap: var(--space-4);
    align-items: stretch;
  }

  .modal-actions {
    justify-content: center;
  }

  .privacy-description {
    padding-left: 0;
  }

  .rating-container {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-2);
  }
}

@media (max-width: 480px) {
  .tags-grid {
    gap: var(--space-1_5);
  }

  .tag {
    padding: var(--space-1) var(--space-2);
    font-size: var(--text-xs);
  }

  .modal-overlay {
    padding: var(--space-2);
  }

  .selection-grid {
    grid-template-columns: 1fr;
  }

  .form-card {
    padding: var(--space-4);
  }
}
</style>
