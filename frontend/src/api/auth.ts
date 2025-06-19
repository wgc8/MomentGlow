import http from '@/utils/http'

export interface RegisterData {
  username: string
  password: string
  password2: string
  email: string
}

export interface LoginData {
  username: string
  password: string
}

export interface LoginResponse {
  token: string
  refresh: string
  user: {
    id: number
    username: string
    email: string
  }
}

export interface RefreshTokenResponse {
  access: string
}

export const register = async (data: RegisterData) => {
  try {
    const response = await http.post('api/user/register/', data)
    return response.data
  } catch (error: any) {
    if (error.response) {
      throw error.response.data
    }
    throw error
  }
}

export const login = async (data: LoginData) => {
  try {
    const response = await http.post<LoginResponse>('api/user/login/', data)
    return response
  } catch (error: any) {
    if (error.response) {
      throw error.response.data
    }
    throw error
  }
}

export const refreshToken = async (refresh: string) => {
  try {
    const response = await http.post<RefreshTokenResponse>('api/user/token/refresh/', { refresh })
    return response
  } catch (error: any) {
    if (error.response) {
      throw error.response.data
    }
    throw error
  }
} 