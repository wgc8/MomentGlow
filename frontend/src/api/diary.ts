import request from '@/utils/http'

export interface DiaryInput {
  id?: number
  title?: string
  content: string
  mood: string
  weather: string
  is_public: boolean
  user?: {
    id: string
    username: string
    // avatar: string
  }
  // likes: number
  // comments: number
  // isLiked: boolean
}

export interface GetDiariesRequestParams {
  user_id?: string
  page?: number
  mood?: string
  timeRange?: string
}

export interface GetPublicDiariesResponse {
  code: number
  errMsg: string
  data: {
    next: string
    previous: string
    count: number
    results: []
  }
}

// 获取公开日记列表
export const getDiaries= (params: GetDiariesRequestParams) => {
  return request.get<GetPublicDiariesResponse>('/api/diaries/', { params })
}

// 获取公开日记列表
export const getPublicDiaries= (params: GetDiariesRequestParams) => {
  return request.get<GetPublicDiariesResponse>('/api/diaries/public/', { params })
}

// 点赞日记
export const likeDiary = (diaryId: number) => {
  return request.post(`/api/diaries/${diaryId}/like/`)
}

// 取消点赞日记
export const unlikeDiary = (diaryId: number) => {
  return request.delete(`/api/diaries/${diaryId}/like/`)
}

// 获取日记评论
export const getDiaryComments = (diaryId: number) => {
  return request.get(`/api/diaries/${diaryId}/comments/`)
}

// 发表评论
export const addComment = (diaryId: number, content: string) => {
  return request.post(`/api/diaries/${diaryId}/add_comment/`, { content })
} 

// 发布日记
export const publishDiary = (diary: DiaryInput) => {
  return request.post('/api/diaries/', diary)
}

// 修改日记
export const updateDiary = (diary: DiaryInput) => {
  return request.put(`/api/diaries/${diary.id}/`, diary)
}

// 删除日记
export const deleteDiary = (diaryId: number) => {
  return request.delete(`/api/diaries/${diaryId}/`)
}

// 修改日记
