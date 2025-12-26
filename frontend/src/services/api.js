// API service for dream project backend communication

// 使用 Vite 环境变量
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8888'

// Auth API endpoints
export const AUTH_ENDPOINTS = {
  LOGIN: `${API_BASE_URL}/Auth/Login`,
  SIGN_UP: `${API_BASE_URL}/Auth/Sign`,
  VERIFY: `${API_BASE_URL}/Auth/Verify`,
  RESET_PASSWORD: `${API_BASE_URL}/Auth/ResetPassword`,
  UPDATE_PASSWORD: `${API_BASE_URL}/Auth/UpdatePassword`,
}

// User API endpoints
export const USER_ENDPOINTS = {
  GET_INFO: `${API_BASE_URL}/User/GetInfo`,
  UPDATE_INFO: `${API_BASE_URL}/User/UpdateInfo`,
  UPLOAD_AVATAR: `${API_BASE_URL}/User/UploadAvatar`,
  GET_STATISTICS: `${API_BASE_URL}/User/GetStatistics`,
}

// Dream API endpoints
export const DREAM_ENDPOINTS = {
  CREATE: `${API_BASE_URL}/Dream/Create`,
  GET_LIST: `${API_BASE_URL}/Dream/GetList`,
  GET_DETAIL: `${API_BASE_URL}/Dream/GetDetail`,
  UPDATE: `${API_BASE_URL}/Dream/Update`,
  DELETE: `${API_BASE_URL}/Dream/Delete`,
  GET_EMOTIONS: `${API_BASE_URL}/Dream/GetEmotions`,
  GET_DREAM_TYPES: `${API_BASE_URL}/Dream/GetDreamTypes`,
}

// Analysis API endpoints
export const ANALYSIS_ENDPOINTS = {
  CREATE: `${API_BASE_URL}/Analysis/Create`,
  GET_LIST: `${API_BASE_URL}/Analysis/GetList`,
  GET_DETAIL: `${API_BASE_URL}/Analysis/GetDetail`,
  DELETE: `${API_BASE_URL}/Analysis/Delete`,
}

// AI API endpoints
export const AI_ENDPOINTS = {
  EXTRACT_KEYWORDS: `${API_BASE_URL}/AI/ExtractKeywords`,
  ANALYZE_DREAM: `${API_BASE_URL}/AI/AnalyzeDream`,
  CHAT: `${API_BASE_URL}/AI/Chat`,
  GENERATE_SUMMARY: `${API_BASE_URL}/AI/GenerateSummary`,
  GET_EMOTION_SUGGESTIONS: `${API_BASE_URL}/AI/GetEmotionSuggestions`,
  ANALYZE_WITH_KEYWORDS: `${API_BASE_URL}/AI/AnalyzeDreamWithKeywords`,
  GET_CHAT_HISTORY: `${API_BASE_URL}/AI/GetChatHistory`,
  SAVE_CHAT_HISTORY: `${API_BASE_URL}/AI/SaveChatHistory`,
  DELETE_CHAT_HISTORY: `${API_BASE_URL}/AI/DeleteChatHistory`,
}

/**
 * Login user
 * @param {string} email - User email
 * @param {string} password - User password
 * @returns {Promise} - Login response
 */
export async function login(email, password) {
  const response = await fetch(AUTH_ENDPOINTS.LOGIN, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      Email: email,
      Password: password
    })
  })

  return await response.json()
}

/**
 * Direct sign up (no verification code needed)
 * @param {string} name - User name
 * @param {string} email - User email
 * @param {string} password - User password
 * @returns {Promise} - Sign up response
 */
export async function signUp(name, email, password) {
  const response = await fetch(AUTH_ENDPOINTS.SIGN_UP, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      Name: name,
      Email: email,
      Password: password
    })
  })

  return await response.json()
}

/**
 * Verify sign up with code
 * @param {string} name - User name
 * @param {string} email - User email
 * @param {string} password - User password
 * @param {string} verifyCode - Verification code
 * @returns {Promise} - Verification response
 */
export async function verifySignUp(name, email, password, verifyCode) {
  const response = await fetch(AUTH_ENDPOINTS.VERIFY, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      Name: name,
      Email: email,
      Password: password,
      VerifyCode: verifyCode
    })
  })

  return await response.json()
}

/**
 * Request password reset (send verification code)
 * @param {string} email - User email
 * @returns {Promise} - Reset password response
 */
export async function requestPasswordReset(email) {
  const response = await fetch(AUTH_ENDPOINTS.RESET_PASSWORD, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      Email: email,
      Password: '' // 密码在发送验证码阶段不需要提供
    })
  })

  return await response.json()
}

/**
 * Update password (with verification code)
 * @param {string} email - User email
 * @param {string} password - New password
 * @param {string} verifyCode - Verification code
 * @returns {Promise} - Update password response
 */
export async function updatePassword(email, password, verifyCode) {
  const response = await fetch(AUTH_ENDPOINTS.UPDATE_PASSWORD, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      Email: email,
      Password: password,
      VerifyCode: verifyCode
    })
  })

  return await response.json()
}

/**
 * Check JWT Token validity
 * @param {string} token - JWT token
 * @returns {Promise} - Token validation response
 */
export async function checkToken(token) {
  const response = await fetch(`${API_BASE_URL}/CheckJWTToken`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  })

  return await response.json()
}

/**
 * Get current user information
 * @param {string} token - JWT token
 * @returns {Promise} - User info response
 */
export async function getUserInfo(token) {
  const response = await fetch(USER_ENDPOINTS.GET_INFO, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  })

  return await response.json()
}

/**
 * Get user statistics data
 * @param {string} token - JWT token
 * @returns {Promise} - User statistics response
 */
export async function getUserStatistics(token) {
  const response = await fetch(USER_ENDPOINTS.GET_STATISTICS, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  })

  return await response.json()
}

/**
 * Update user information
 * @param {object} userInfo - User info to update { userName, gender, birthDate, phone, address }
 * @param {string} token - JWT token
 * @returns {Promise} - Update user info response
 */
export async function updateUserInfo(userInfo, token) {
  const response = await fetch(USER_ENDPOINTS.UPDATE_INFO, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(userInfo)
  })

  return await response.json()
}

/**
 * Upload user avatar
 * @param {FormData} formData - FormData containing avatar file
 * @param {string} token - JWT token
 * @returns {Promise} - Upload avatar response
 */
export async function uploadAvatar(formData, token) {
  const response = await fetch(USER_ENDPOINTS.UPLOAD_AVATAR, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
      // Don't set Content-Type header for FormData, it will be set automatically
    },
    body: formData
  })

  return await response.json()
}

// Dream related API functions

/**
 * Create a dream entry
 * @param {object} payload - Dream data { title, content, tags, isPublic, dreamDate }
 * @param {string} token - JWT token
 * @returns {Promise} - Create dream response
 */
export async function createDream(payload, token) {
  const response = await fetch(DREAM_ENDPOINTS.CREATE, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(payload)
  })

  return await response.json()
}

/**
 * Get user's dreams list
 * @param {string} token - JWT token
 * @param {object} params - Query parameters { page, pageSize, dateFrom, dateTo, keyword }
 * @returns {Promise} - Dreams list response
 */
export async function getDreamsList(token, params = {}) {
  const queryString = new URLSearchParams(params).toString()
  const url = queryString ? `${DREAM_ENDPOINTS.GET_LIST}?${queryString}` : DREAM_ENDPOINTS.GET_LIST

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  })

  return await response.json()
}

/**
 * Get dream detail
 * @param {number} dreamId - Dream ID
 * @param {string} token - JWT token
 * @returns {Promise} - Dream detail response
 */
export async function getDreamDetail(dreamId, token) {
  const response = await fetch(`${DREAM_ENDPOINTS.GET_DETAIL}/${dreamId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  })

  return await response.json()
}

/**
 * Update dream entry
 * @param {number} dreamId - Dream ID
 * @param {object} payload - Updated dream data
 * @param {string} token - JWT token
 * @returns {Promise} - Update dream response
 */
export async function updateDream(dreamId, payload, token) {
  const response = await fetch(`${DREAM_ENDPOINTS.UPDATE}/${dreamId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(payload)
  })

  return await response.json()
}

/**
 * Delete dream entry
 * @param {number} dreamId - Dream ID
 * @param {string} token - JWT token
 * @returns {Promise} - Delete dream response
 */
export async function deleteDream(dreamId, token) {
  const response = await fetch(`${DREAM_ENDPOINTS.DELETE}/${dreamId}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  })

  return await response.json()
}

/**
 * Search dreams
 * @param {object} filters - Search filters { keyword, tags, dateFrom, dateTo }
 * @param {string} token - JWT token
 * @returns {Promise} - Search results response
 */
export async function searchDreams(filters, token) {
  const response = await fetch(DREAM_ENDPOINTS.SEARCH, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(filters)
  })

  return await response.json()
}

/**
 * Get all emotions
 * @param {string} token - JWT token
 * @returns {Promise} - Emotions list response
 */
export async function getEmotions(token) {
  const response = await fetch(DREAM_ENDPOINTS.GET_EMOTIONS, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  })

  return await response.json()
}

/**
 * Get all dream types
 * @param {string} token - JWT token
 * @returns {Promise} - Dream types list response
 */
export async function getDreamTypes(token) {
  const response = await fetch(DREAM_ENDPOINTS.GET_DREAM_TYPES, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  })

  return await response.json()
}

/**
 * Create dream analysis
 * @param {object} payload - Analysis data { startDate, endDate, result, recommendation }
 * @param {string} token - JWT token
 * @returns {Promise} - Create analysis response
 */
export async function createAnalysis(payload, token) {
  const response = await fetch(ANALYSIS_ENDPOINTS.CREATE, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(payload)
  })

  return await response.json()
}

/**
 * Get user's analysis list
 * @param {string} token - JWT token
 * @param {object} params - Query parameters { page, pageSize }
 * @returns {Promise} - Analysis list response
 */
export async function getAnalysisList(token, params = {}) {
  const queryString = new URLSearchParams(params).toString()
  const url = queryString ? `${ANALYSIS_ENDPOINTS.GET_LIST}?${queryString}` : ANALYSIS_ENDPOINTS.GET_LIST

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  })

  return await response.json()
}

/**
 * Get analysis detail
 * @param {number} analysisId - Analysis ID
 * @param {string} token - JWT token
 * @returns {Promise} - Analysis detail response
 */
export async function getAnalysisDetail(analysisId, token) {
  const response = await fetch(`${ANALYSIS_ENDPOINTS.GET_DETAIL}/${analysisId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  })

  return await response.json()
}

/**
 * Delete analysis
 * @param {number} analysisId - Analysis ID
 * @param {string} token - JWT token
 * @returns {Promise} - Delete analysis response
 */
export async function deleteAnalysis(analysisId, token) {
  const response = await fetch(`${ANALYSIS_ENDPOINTS.DELETE}/${analysisId}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  })

  return await response.json()
}

/**
 * Share dream (make public/private)
 * @param {number} dreamId - Dream ID
 * @param {boolean} isPublic - Whether dream should be public
 * @param {string} token - JWT token
 * @returns {Promise} - Share dream response
 */
export async function shareDream(dreamId, isPublic, token) {
  const response = await fetch(`${DREAM_ENDPOINTS.SHARE}/${dreamId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      isPublic: isPublic
    })
  })

  return await response.json()
}

// ==================== AI 相关API ====================

/**
 * 提取梦境关键词
 * @param {string} content - 梦境内容
 * @param {string} token - JWT token
 * @returns {Promise} - 关键词提取结果 { keywords, emotions, dreamTypes }
 */
export async function extractKeywords(content, token) {
  const response = await fetch(AI_ENDPOINTS.EXTRACT_KEYWORDS, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ content })
  })

  return await response.json()
}

/**
 * 分析梦境
 * @param {string} content - 梦境内容
 * @param {string} context - 额外上下文（可选）
 * @param {string} token - JWT token
 * @returns {Promise} - 分析结果
 */
export async function analyzeDream(content, token, context = '') {
  const response = await fetch(AI_ENDPOINTS.ANALYZE_DREAM, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ content, context })
  })

  return await response.json()
}

/**
 * AI对话
 * @param {string} question - 用户问题
 * @param {string} dreamContext - 梦境内容/分析报告
 * @param {Array} chatHistory - 对话历史（可选）
 * @param {string} token - JWT token
 * @returns {Promise} - AI回复
 */
export async function aiChat(question, dreamContext, token, chatHistory = []) {
  const response = await fetch(AI_ENDPOINTS.CHAT, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      question,
      dreamContext,
      chatHistory
    })
  })

  return await response.json()
}

/**
 * 生成多梦总结
 * @param {Array} dreams - 梦境列表
 * @param {string} token - JWT token
 * @returns {Promise} - 总结结果
 */
export async function generateDreamSummary(dreams, token) {
  const response = await fetch(AI_ENDPOINTS.GENERATE_SUMMARY, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ dreams })
  })

  return await response.json()
}

/**
 * 获取情绪建议
 * @param {Array} emotions - 情绪列表
 * @param {string} token - JWT token
 * @returns {Promise} - 建议内容
 */
export async function getEmotionSuggestions(emotions, token) {
  const response = await fetch(AI_ENDPOINTS.GET_EMOTION_SUGGESTIONS, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ emotions })
  })

  return await response.json()
}

/**
 * 分析梦境并提取关键词（组合接口）
 * @param {string} content - 梦境内容
 * @param {string} token - JWT token
 * @param {string} context - 额外上下文（可选）
 * @returns {Promise} - 分析结果（包含关键词和分析）
 */
export async function analyzeDreamWithKeywords(content, token, context = '') {
  const response = await fetch(AI_ENDPOINTS.ANALYZE_WITH_KEYWORDS, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ content, context })
  })

  return await response.json()
}

/**
 * 获取AI对话历史
 * @param {string} sourceType - 来源类型 (dream/analysis)
 * @param {number} sourceId - 梦境ID或分析ID
 * @param {string} token - JWT token
 * @returns {Promise} - 对话历史
 */
export async function getAIChatHistory(sourceType, sourceId, token) {
  const response = await fetch(`${AI_ENDPOINTS.GET_CHAT_HISTORY}?sourceType=${sourceType}&sourceId=${sourceId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  })

  return await response.json()
}

/**
 * 保存AI对话历史
 * @param {string} sourceType - 来源类型 (dream/analysis)
 * @param {number} sourceId - 梦境ID或分析ID
 * @param {Array} messages - 对话消息列表
 * @param {string} token - JWT token
 * @returns {Promise} - 保存结果
 */
export async function saveAIChatHistory(sourceType, sourceId, messages, token) {
  const response = await fetch(AI_ENDPOINTS.SAVE_CHAT_HISTORY, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      sourceType,
      sourceId,
      messages
    })
  })

  return await response.json()
}

/**
 * 删除AI对话历史
 * @param {string} sourceType - 来源类型 (dream/analysis)
 * @param {number} sourceId - 梦境ID或分析ID
 * @param {string} token - JWT token
 * @returns {Promise} - 删除结果
 */
export async function deleteAIChatHistory(sourceType, sourceId, token) {
  const response = await fetch(AI_ENDPOINTS.DELETE_CHAT_HISTORY, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      sourceType,
      sourceId
    })
  })

  return await response.json()
}

// ==================== Admin API ====================

// Admin API endpoints
export const ADMIN_ENDPOINTS = {
  LOGIN: `${API_BASE_URL}/Admin/Login`,
  GET_LOGS: `${API_BASE_URL}/Admin/GetLogs`,
  DELETE_LOGS: `${API_BASE_URL}/Admin/DeleteLogs`,
  GET_EMOTIONS: `${API_BASE_URL}/Admin/GetEmotions`,
  ADD_EMOTION: `${API_BASE_URL}/Admin/AddEmotion`,
  DELETE_EMOTION: (id) => `${API_BASE_URL}/Admin/DeleteEmotion/${id}`,
  GET_DREAM_TYPES: `${API_BASE_URL}/Admin/GetDreamTypes`,
  ADD_DREAM_TYPE: `${API_BASE_URL}/Admin/AddDreamType`,
  DELETE_DREAM_TYPE: (id) => `${API_BASE_URL}/Admin/DeleteDreamType/${id}`,
  GET_PUBLIC_DREAMS: `${API_BASE_URL}/Admin/GetPublicDreams`,
}

/**
 * 管理员登录
 * @param {string} email - 管理员邮箱
 * @param {string} password - 密码
 * @returns {Promise} - 登录结果
 */
export async function adminLogin(email, password) {
  const response = await fetch(ADMIN_ENDPOINTS.LOGIN, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      Email: email,
      Password: password
    })
  })

  return await response.json()
}

/**
 * 获取日志列表
 * @param {string} token - JWT token
 * @param {object} params - 查询参数 { logType, startDate, endDate, page, pageSize }
 * @returns {Promise} - 日志列表
 */
export async function getLogs(token, params = {}) {
  const queryString = new URLSearchParams(params).toString()
  const url = queryString ? `${ADMIN_ENDPOINTS.GET_LOGS}?${queryString}` : ADMIN_ENDPOINTS.GET_LOGS

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  })

  return await response.json()
}

/**
 * 批量删除日志
 * @param {Array} logIds - 日志ID列表
 * @param {string} token - JWT token
 * @returns {Promise} - 删除结果
 */
export async function deleteLogs(logIds, token) {
  const response = await fetch(ADMIN_ENDPOINTS.DELETE_LOGS, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      logIds
    })
  })

  return await response.json()
}

/**
 * 获取所有情绪
 * @param {string} token - JWT token
 * @returns {Promise} - 情绪列表
 */
export async function adminGetEmotions(token) {
  const response = await fetch(ADMIN_ENDPOINTS.GET_EMOTIONS, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  })

  return await response.json()
}

/**
 * 添加新情绪
 * @param {object} data - 情绪数据 { emotionName, color }
 * @param {string} token - JWT token
 * @returns {Promise} - 添加结果
 */
export async function adminAddEmotion(data, token) {
  const response = await fetch(ADMIN_ENDPOINTS.ADD_EMOTION, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      EmotionName: data.emotionName,
      Color: data.color
    })
  })

  return await response.json()
}

/**
 * 删除情绪
 * @param {number} emotionId - 情绪ID
 * @param {string} token - JWT token
 * @returns {Promise} - 删除结果
 */
export async function adminDeleteEmotion(emotionId, token) {
  const response = await fetch(ADMIN_ENDPOINTS.DELETE_EMOTION(emotionId), {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  })

  return await response.json()
}

/**
 * 获取所有梦境类型
 * @param {string} token - JWT token
 * @returns {Promise} - 梦境类型列表
 */
export async function adminGetDreamTypes(token) {
  const response = await fetch(ADMIN_ENDPOINTS.GET_DREAM_TYPES, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  })

  return await response.json()
}

/**
 * 添加新梦境类型
 * @param {object} data - 类型数据 { typeName, color }
 * @param {string} token - JWT token
 * @returns {Promise} - 添加结果
 */
export async function adminAddDreamType(data, token) {
  const response = await fetch(ADMIN_ENDPOINTS.ADD_DREAM_TYPE, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      TypeName: data.typeName,
      Color: data.color
    })
  })

  return await response.json()
}

/**
 * 删除梦境类型
 * @param {number} typeId - 类型ID
 * @param {string} token - JWT token
 * @returns {Promise} - 删除结果
 */
export async function adminDeleteDreamType(typeId, token) {
  const response = await fetch(ADMIN_ENDPOINTS.DELETE_DREAM_TYPE(typeId), {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  })

  return await response.json()
}

/**
 * 获取所有公开梦境
 * @param {string} token - JWT token
 * @param {object} params - 查询参数 { page, pageSize }
 * @returns {Promise} - 公开梦境列表
 */
export async function getPublicDreams(token, params = {}) {
  const queryString = new URLSearchParams(params).toString()
  const url = queryString ? `${ADMIN_ENDPOINTS.GET_PUBLIC_DREAMS}?${queryString}` : ADMIN_ENDPOINTS.GET_PUBLIC_DREAMS

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  })

  return await response.json()
}