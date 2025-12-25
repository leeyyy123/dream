<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { aiChat, analyzeDream, getDreamDetail, getAIChatHistory, saveAIChatHistory } from '../services/api'
import {
  ArrowLeft,
  ChatLineRound,
  User,
  Promotion,
  Loading
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

// 响应式数据
const loading = ref(false)
const sending = ref(false)
const error = ref('')
const dreamContent = ref('')
const analysisContent = ref('')

// 聊天相关
const messages = ref([])
const userQuestion = ref('')
const chatContainer = ref(null)

// 来源类型（从梦境详情或分析报告进入）
const sourceType = ref('dream') // 'dream' 或 'analysis'
const sourceId = ref(null)

// 获取聊天标题
const chatTitle = ref('梦境分析助手')
const chatSubtitle = ref('你可以问我关于梦境的任何问题')

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

// 初始化
onMounted(async () => {
  // 从路由参数获取来源信息
  sourceType.value = route.query.source || 'dream'
  sourceId.value = route.query.id

  if (sourceType.value === 'dream' && sourceId.value) {
    chatTitle.value = '梦境分析助手'
    chatSubtitle.value = '基于梦境内容，我可以为你深入分析和解答疑惑'
    await loadDreamContent()
  } else if (sourceType.value === 'analysis' && sourceId.value) {
    chatTitle.value = '分析报告助手'
    chatSubtitle.value = '基于分析报告，我可以为你提供更多解读和建议'
    await loadAnalysisContent()
  }

  // 添加欢迎消息
  addMessage('assistant', `你好！我是你的${chatTitle.value}。${chatSubtitle.value}。请问有什么我可以帮助你的吗？`)
})

// 加载梦境内容
const loadDreamContent = async () => {
  loading.value = true
  error.value = ''

  try {
    const token = localStorage.getItem('authToken')
    if (!token || !sourceId.value) {
      error.value = '缺少必要参数'
      return
    }

    const response = await getDreamDetail(sourceId.value, token)

    if (response.Code === 200 && response.Data) {
      const dream = response.Data

      // 格式化日期
      const formatDate = (dateString) => {
        if (!dateString) return '未知日期'
        const date = new Date(dateString)
        return date.toLocaleDateString('zh-CN', {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          weekday: 'long'
        })
      }

      // 构建完整的梦境信息
      let content = `【梦境标题】${dream.Title}\n`
      content += `【梦境日期】${formatDate(dream.DreamDate)}\n\n`
      content += `【梦境内容】\n${dream.Content}\n\n`

      // 添加睡眠评估
      content += `【睡眠评估】\n`
      content += `- 睡眠质量：${getSleepQualityText(dream.SleepQuality)}\n`
      content += `- 梦境清晰度：${getLucidityText(dream.LucidityLevel)}\n\n`

      // 添加情绪标签
      if (dream.Emotions && dream.Emotions.length > 0) {
        content += `【情绪标签】\n`
        dream.Emotions.forEach(emotion => {
          const intensityDesc = emotion.Intensity ? `(强度:${emotion.Intensity}/10)` : ''
          const primaryMark = emotion.IsPrimary ? ' [主导情绪]' : ''
          content += `- ${emotion.EmotionName}${intensityDesc}${primaryMark}\n`
        })
        content += '\n'
      }

      // 添加梦境类型
      if (dream.DreamTypes && dream.DreamTypes.length > 0) {
        content += `【梦境类型】\n`
        dream.DreamTypes.forEach(type => {
          const confidenceDesc = type.Confidence ? `(置信度:${Math.round(type.Confidence * 100)}%)` : ''
          content += `- ${type.TypeName}${confidenceDesc}\n`
        })
      }

      dreamContent.value = content

      // 加载对话历史
      await loadChatHistory(token)

      // 如果没有历史记录，添加欢迎消息
      if (messages.value.length === 0) {
        let welcomeMsg = `我看到你记录了梦境《${dream.Title}》，发生在${formatDate(dream.DreamDate)}。`
        welcomeMsg += `\n\n睡眠质量：${getSleepQualityText(dream.SleepQuality)}，梦境清晰度：${getLucidityText(dream.LucidityLevel)}`

        if (dream.Emotions && dream.Emotions.length > 0) {
          const emotionNames = dream.Emotions.map(e => e.EmotionName).join('、')
          welcomeMsg += `\n梦中情绪：${emotionNames}`
        }

        if (dream.DreamTypes && dream.DreamTypes.length > 0) {
          const typeNames = dream.DreamTypes.map(t => t.TypeName).join('、')
          welcomeMsg += `\n梦境类型：${typeNames}`
        }

        welcomeMsg += `\n\n你可以问我关于这个梦境的任何问题，比如：\n\n• 这个梦境可能代表什么含义？\n• 梦中的某些元素有什么象征意义？\n• 这些情绪和我的生活有什么关系？\n• 这个日期有什么特殊意义吗？`

        addMessage('assistant', welcomeMsg)
      }
    } else {
      error.value = response.Msg || '加载梦境失败'
    }
  } catch (err) {
    console.error('加载梦境失败:', err)
    error.value = '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 加载对话历史
const loadChatHistory = async (token) => {
  try {
    const response = await getAIChatHistory(sourceType.value, sourceId.value, token)

    if (response.Code === 200 && response.Data) {
      const historyMessages = response.Data.Messages || []

      if (historyMessages.length > 0) {
        // 恢复历史消息
        historyMessages.forEach(msg => {
          messages.value.push({
            role: msg.role,
            content: msg.content,
            timestamp: new Date(msg.timestamp || new Date())
          })
        })

        // 滚动到底部
        setTimeout(() => {
          if (chatContainer.value) {
            chatContainer.value.scrollTop = chatContainer.value.scrollHeight
          }
        }, 100)

        console.log(`已加载 ${historyMessages.length} 条历史消息`)
      }
    }
  } catch (err) {
    console.error('加载对话历史失败:', err)
    // 加载历史失败不影响正常使用
  }
}

// 保存对话历史
const saveHistoryToServer = async () => {
  try {
    const token = localStorage.getItem('authToken')
    if (!token || !sourceId.value) return

    // 准备要保存的消息数据
    const messagesToSave = messages.value.map(msg => ({
      role: msg.role,
      content: msg.content,
      timestamp: msg.timestamp.toISOString()
    }))

    const response = await saveAIChatHistory(
      sourceType.value,
      sourceId.value,
      messagesToSave,
      token
    )

    if (response.Code === 200) {
      console.log('对话历史已保存')
    }
  } catch (err) {
    console.error('保存对话历史失败:', err)
    // 保存失败不影响正常使用
  }
}

// 加载分析报告
const loadAnalysisContent = async () => {
  loading.value = true
  error.value = ''

  try {
    // 这里暂时使用模拟数据，你可以根据实际API调整
    analysisContent.value = '分析报告内容'

    addMessage('assistant', '我看到你的梦境分析报告。你可以问我关于报告的任何问题，比如：\n\n• 报告中的某些数据代表什么？\n• 根据这个报告我应该注意什么？\n• 如何改善我的睡眠质量？')
  } catch (err) {
    console.error('加载分析报告失败:', err)
    error.value = '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 添加消息
const addMessage = (role, content) => {
  messages.value.push({
    role,
    content,
    timestamp: new Date()
  })

  // 滚动到底部
  setTimeout(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  }, 100)
}

// 发送消息
const sendMessage = async () => {
  const question = userQuestion.value.trim()
  if (!question || sending.value) return

  // 添加用户消息
  addMessage('user', question)
  userQuestion.value = ''
  sending.value = true

  try {
    const token = localStorage.getItem('authToken')
    if (!token) {
      addMessage('assistant', '抱歉，登录状态已失效，请重新登录')
      return
    }

    // 构建上下文
    const context = dreamContent.value || analysisContent.value || ''

    // 获取聊天历史（最近10条消息）
    const chatHistory = messages.value.slice(-10).map(msg => ({
      role: msg.role === 'assistant' ? 'assistant' : 'user',
      content: msg.content
    }))

    // 调用AI对话接口
    const response = await aiChat(question, context, token, chatHistory)

    if (response.Code === 200 && response.Data) {
      addMessage('assistant', response.Data.reply)
    } else {
      addMessage('assistant', '抱歉，我遇到了一些问题。请稍后再试。')
    }
  } catch (err) {
    console.error('AI对话失败:', err)
    addMessage('assistant', '抱歉，网络连接出现问题。请检查网络后重试。')
  } finally {
    sending.value = false
  }
}

// 监听消息变化，自动保存
watch(messages, () => {
  // 只在有有效sourceId且有消息时才保存
  if (sourceId.value && messages.value.length > 0) {
    saveHistoryToServer()
  }
}, { deep: true })

// 快捷问题
const quickQuestions = ref([
  '这个梦境可能代表什么含义？',
  '梦中的某些元素有什么象征意义？',
  '这个梦境和我的情绪有什么关系？',
  '根据这个梦境我应该注意什么？'
])

const sendQuickQuestion = (question) => {
  userQuestion.value = question
  sendMessage()
}

// 返回
const goBack = () => {
  if (sourceType.value === 'dream' && sourceId.value) {
    router.push('/main/my-dreams')
  } else {
    router.push('/main/dream-analysis')
  }
}

// 格式化时间
const formatTime = (date) => {
  return new Date(date).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<template>
  <div class="ai-chat-container">
    <!-- 头部 -->
    <header class="header">
      <div class="container">
        <div class="header-content">
          <button class="back-button" @click="goBack">
            <component :is="ArrowLeft" class="back-icon" />
            <span>返回</span>
          </button>
          <div class="header-info">
            <h1 class="page-title">{{ chatTitle }}</h1>
            <p class="page-subtitle">{{ chatSubtitle }}</p>
          </div>
          <div class="header-spacer"></div>
        </div>
      </div>
    </header>

    <!-- 主内容 -->
    <main class="main-content">
      <div class="container">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-section">
          <div class="loading-spinner"></div>
          <span>加载中...</span>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="error" class="error-section">
          <p class="error-message">{{ error }}</p>
          <button class="spa-button-primary" @click="goBack">返回</button>
        </div>

        <!-- 聊天界面 -->
        <div v-else class="chat-layout">
          <!-- 消息列表 -->
          <div ref="chatContainer" class="messages-container">
            <div
              v-for="(message, index) in messages"
              :key="index"
              :class="['message', `message-${message.role}`]"
            >
              <div class="message-avatar">
                <component
                  :is="message.role === 'user' ? User : Promotion"
                  class="avatar-icon"
                />
              </div>
              <div class="message-content">
                <div class="message-text">{{ message.content }}</div>
                <div class="message-time">{{ formatTime(message.timestamp) }}</div>
              </div>
            </div>

            <!-- 发送中提示 -->
            <div v-if="sending" class="message message-assistant">
              <div class="message-avatar">
                <component :is="Promotion" class="avatar-icon" />
              </div>
              <div class="message-content">
                <div class="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>

          <!-- 快捷问题 -->
          <div class="quick-questions">
            <div class="quick-questions-title">你可以问我：</div>
            <div class="quick-questions-list">
              <button
                v-for="(question, idx) in quickQuestions"
                :key="idx"
                class="quick-question-btn"
                @click="sendQuickQuestion(question)"
                :disabled="sending"
              >
                {{ question }}
              </button>
            </div>
          </div>

          <!-- 输入区域 -->
          <div class="input-area">
            <form @submit.prevent="sendMessage" class="input-form">
              <input
                v-model="userQuestion"
                type="text"
                class="message-input"
                placeholder="输入你的问题..."
                :disabled="sending"
                maxlength="500"
              />
              <button
                type="submit"
                class="send-button"
                :disabled="sending || !userQuestion.trim()"
              >
                <component :is="sending ? Loading : ChatLineRound" class="send-icon" />
              </button>
            </form>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.container {
  max-width: 900px;
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

.header-info {
  flex: 1;
}

.page-title {
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  color: var(--neutral-900);
  margin: 0;
}

.page-subtitle {
  font-size: var(--text-sm);
  color: var(--neutral-600);
  margin: var(--space-1) 0 0 0;
}

.header-spacer {
  width: 80px;
}

/* 主内容 */
.main-content {
  padding: var(--space-8) 0;
  height: calc(100vh - 120px);
}

/* 加载和错误状态 */
.loading-section,
.error-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
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

.error-message {
  color: var(--error-600);
  font-size: var(--text-lg);
  margin: 0;
}

/* 聊天布局 */
.chat-layout {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
  border-radius: var(--radius-2xl);
  border: 1px solid var(--border-color);
  overflow: hidden;
}

/* 消息容器 */
.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-6);
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

/* 消息样式 */
.message {
  display: flex;
  gap: var(--space-3);
  max-width: 85%;
}

.message-user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-assistant {
  align-self: flex-start;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message-user .message-avatar {
  background: var(--neutral-900);
  color: white;
}

.message-assistant .message-avatar {
  background: var(--neutral-100);
  color: var(--neutral-700);
}

.avatar-icon {
  width: 18px;
  height: 18px;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.message-text {
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-xl);
  line-height: var(--leading-relaxed);
  word-wrap: break-word;
  white-space: pre-wrap;
}

.message-user .message-text {
  background: var(--neutral-900);
  color: white;
}

.message-assistant .message-text {
  background: var(--neutral-100);
  color: var(--neutral-900);
}

.message-time {
  font-size: var(--text-xs);
  color: var(--neutral-500);
  padding: 0 var(--space-2);
}

/* 打字指示器 */
.typing-indicator {
  display: flex;
  gap: var(--space-1);
  padding: var(--space-3) var(--space-4);
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: var(--neutral-400);
  border-radius: var(--radius-full);
  animation: bounce 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 快捷问题 */
.quick-questions {
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--border-color);
  background: var(--neutral-50);
}

.quick-questions-title {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--neutral-600);
  margin-bottom: var(--space-3);
}

.quick-questions-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.quick-question-btn {
  padding: var(--space-2) var(--space-3);
  background: white;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  font-size: var(--text-sm);
  color: var(--neutral-700);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.quick-question-btn:hover {
  background: var(--neutral-100);
  border-color: var(--border-color-hover);
  color: var(--neutral-900);
}

.quick-question-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.quick-question-btn:disabled:hover {
  background: white;
  border-color: var(--border-color);
  color: var(--neutral-700);
}

/* 输入区域 */
.input-area {
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--border-color);
  background: white;
}

.input-form {
  display: flex;
  gap: var(--space-3);
}

.message-input {
  flex: 1;
  padding: var(--space-3) var(--space-4);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  font-size: var(--text-base);
  outline: none;
  transition: all var(--transition-fast);
}

.message-input:focus {
  border-color: var(--border-color-focus);
  box-shadow: 0 0 0 3px rgb(100 116 139 / 0.1);
}

.message-input:disabled {
  background: var(--neutral-100);
  cursor: not-allowed;
}

.send-button {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-xl);
  background: var(--neutral-900);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.send-button:hover:not(:disabled) {
  background: var(--neutral-800);
  transform: scale(1.05);
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.send-icon {
  width: 20px;
  height: 20px;
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
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    gap: var(--space-4);
  }

  .page-title {
    font-size: var(--text-lg);
  }

  .page-subtitle {
    font-size: var(--text-xs);
  }

  .header-spacer {
    width: 60px;
  }

  .message {
    max-width: 95%;
  }

  .quick-questions-list {
    flex-direction: column;
  }

  .quick-question-btn {
    width: 100%;
    text-align: left;
  }
}
</style>
