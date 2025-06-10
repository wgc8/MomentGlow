import axios from 'axios'
import { useUserStore } from '@/store/user'

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

// 获取用户信息
export const getUserInfo = async (userId: number) => {
  const userStore = useUserStore()
  const response = await axios.get(`/api/users/${userId}`, {
    headers: {
      Authorization: `Bearer ${userStore.token}`
    }
  })
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
  const userStore = useUserStore()
  const response = await axios.put(`/api/users/${userId}`, data, {
    headers: {
      Authorization: `Bearer ${userStore.token}`
    }
  })
  return response.data
}

// 获取用户日记列表
export const getUserDiaries = async (userId: number) => {
  const userStore = useUserStore()
  const response = await axios.get(`/api/users/${userId}/diaries`, {
    headers: {
      Authorization: `Bearer ${userStore.token}`
    }
  })
  return response.data as DiaryEntry[]
}

// 获取用户日记统计数据（用于日历显示）
export interface DiaryStats {
  date: string
  count: number
  mood?: string
}

export const getUserDiaryStats = async (userId: number) => {
  const userStore = useUserStore()
  const response = await axios.get(`/api/users/${userId}/diary-stats`, {
    headers: {
      Authorization: `Bearer ${userStore.token}`
    }
  })
  return response.data as DiaryStats[]
}

// 更新日记内容
export const updateDiary = async (diaryId: number, content: string, mood: string) => {
  const userStore = useUserStore()
  const response = await axios.put(`/api/diaries/${diaryId}`, { content, mood }, {
    headers: {
      Authorization: `Bearer ${userStore.token}`
    }
  })
  return response.data
}

// 删除日记
export const deleteDiary = async (diaryId: number) => {
  const userStore = useUserStore()
  await axios.delete(`/api/diaries/${diaryId}`, {
    headers: {
      Authorization: `Bearer ${userStore.token}`
    }
  })
} 