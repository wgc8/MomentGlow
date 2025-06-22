import http from '@/utils/http'

// 用户信息类型
export interface UserInfo {
  id: number
  username: string
  email: string
  avatar?: string
  bio?: string
  createdAt: string
}

// 日记条目类型
export interface DiaryEntry {
  id: number
  userId: number
  content: string
  mood: string
  createdAt: string
  updatedAt: string
}

// 获取用户日记统计数据（用于日历显示）
export interface DiaryStats {
  date: string
  count: number
  mood?: string
}

// 获取用户信息
export const getUserInfo = async (userId: number) => {
  const response = await http.get(`/api/users/${userId}`)
  return response.data as UserInfo
}

// 更新用户信息
export interface UpdateUserData {
  username?: string
  email?: string
  avatar?: string
  bio?: string
}

export const updateUserInfo = async (userId: number, data: UpdateUserData) => {
  const response = await http.put(`/api/users/${userId}`, data)
  return response.data
}

// 获取用户日记列表
export const getUserDiaries = async (userId: number) => {
  const response = await http.get(`/api/users/${userId}/diaries`)
  return response.data as DiaryEntry[]
}

export const getUserDiaryStats = async (userId: number) => {
  const response = await http.get(`/api/users/${userId}/diary-stats`)
  return response.data as DiaryStats[]
}

// 更新日记内容
export const updateDiary = async (diaryId: number, content: string, mood: string) => {
  const response = await http.put(`/api/diaries/${diaryId}`, { content, mood })
  return response.data
}

// 删除日记
export const deleteDiary = async (diaryId: number) => {
  await http.delete(`/api/diaries/${diaryId}`)
} 