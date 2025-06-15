import request from '@/utils/http'

export interface Diary {
  id: number
  content: string
  mood: string
  createdAt: string
  user: {
    id: number
    username: string
    avatar: string
  }
  likes: number
  comments: number
  isLiked: boolean
}

export interface GetPublicDiariesParams {
  page: number
  mood?: string
  timeRange?: string
}

export interface GetPublicDiariesResponse {
  data: Diary[]
  hasMore: boolean
}

// 获取公开日记列表
export const getPublicDiaries = (params: GetPublicDiariesParams) => {
  return request.get<GetPublicDiariesResponse>('/api/diaries/public', { params })
}

// 点赞日记
export const likeDiary = (diaryId: number) => {
  return request.post(`/api/diaries/${diaryId}/like`)
}

// 取消点赞日记
export const unlikeDiary = (diaryId: number) => {
  return request.delete(`/api/diaries/${diaryId}/like`)
}

// 获取日记评论
export const getDiaryComments = (diaryId: number) => {
  return request.get(`/api/diaries/${diaryId}/comments`)
}

// 发表评论
export const addComment = (diaryId: number, content: string) => {
  return request.post(`/api/diaries/${diaryId}/comments`, { content })
} 