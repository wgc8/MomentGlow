// 心情类型定义
export const MOOD_TYPES = {
  HAPPY: 'happy',
  SAD: 'sad',
  ANGRY: 'angry',
  CALM: 'calm',
  EXCITED: 'excited',
  ANXIOUS: 'anxious',
  TIRED: 'tired'
} as const

// 心情文本映射
export const MOOD_TEXT_MAP: Record<string, string> = {
  [MOOD_TYPES.HAPPY]: '开心',
  [MOOD_TYPES.SAD]: '难过',
  [MOOD_TYPES.ANGRY]: '生气',
  [MOOD_TYPES.CALM]: '平静',
  [MOOD_TYPES.EXCITED]: '兴奋',
  [MOOD_TYPES.ANXIOUS]: '焦虑',
  [MOOD_TYPES.TIRED]: '疲惫'
}

// API端点常量
export const API_ENDPOINTS = {
  LOGIN: '/api/users/login/',
  REGISTER: '/api/users/register/',
  DIARIES: '/api/diaries/',
  PROFILE: '/api/users/profile/'
}