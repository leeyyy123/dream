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