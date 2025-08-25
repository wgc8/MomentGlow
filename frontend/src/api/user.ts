import http from '@/utils/http'

// 用户信息类型
export interface UserInfo {
  id: number
  username: string
  email: string
  avatar?: string
  avatar_url?: string
  bio?: string
  date_joined: string
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

// 头像信息类型
export interface AvatarInfo {
  avatar_url: string
  has_avatar: boolean
}

// 获取用户信息
export const getUserInfo = async (userId: number) => {
  const response = await http.get(`/api/users/profiles/${userId}/`)
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
  const response = await http.put(`/api/users/profiles/${userId}/`, data)
  return response.data
}

// 获取用户头像
export const getUserAvatar = async (userId?: number) => {
  const url = userId ? `/api/users/avatar/${userId}/` : '/api/users/avatar/'
  const response = await http.get(url)
  return response.data as AvatarInfo
}

// 上传用户头像
export const uploadUserAvatar = async (file: File) => {
  const formData = new FormData()
  formData.append('avatar', file)
  
  const response = await http.post('/api/users/avatar/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

// // 获取用户日记列表
// export const getUserDiaries = async (userId: number) => {
//   const response = await http.get(`/api/users/${userId}/diaries`)
//   return response.data as DiaryEntry[]
// }

// export const getUserDiaryStats = async (userId: number) => {
//   const response = await http.get(`/api/users/${userId}/diary-stats`)
//   return response.data as DiaryStats[]
// }

// // 更新日记内容
// export const updateDiary = async (diaryId: number, content: string, mood: string) => {
//   const response = await http.put(`/api/diaries/${diaryId}`, { content, mood })
//   return response.data
// }

// // 删除日记
// export const deleteDiary = async (diaryId: number) => {
//   await http.delete(`/api/diaries/${diaryId}`)
// } 