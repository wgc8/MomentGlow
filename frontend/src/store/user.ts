import { defineStore } from 'pinia'
import { login as apiLogin, refreshToken as apiRefreshToken } from '@/api/auth'
import type { LoginData, LoginResponse } from '@/api/auth'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem('token') || '')
  const refreshToken = ref<string>(localStorage.getItem('refreshToken') || '')
  const userId = ref<number | null>(localStorage.getItem('userId') ? parseInt(localStorage.getItem('userId') || '0') : null)
  const username = ref<string>(localStorage.getItem('username') || '')
  const isLoggedIn = ref<boolean>(localStorage.getItem('isLoggedIn') === 'true')

  // 登录
  const login = async (loginData: LoginData) => {
    try {
      const response = await apiLogin(loginData)
      setUserInfo(response)
      return response
    } catch (error) {
      throw error
    }
  }

  // 设置用户信息
  const setUserInfo = (data: LoginResponse) => {
    token.value = data.token
    refreshToken.value = data.refresh
    userId.value = data.user.id
    username.value = data.user.username
    isLoggedIn.value = true

    // 保存到本地存储
    localStorage.setItem('token', data.token)
    localStorage.setItem('refreshToken', data.refresh)
    localStorage.setItem('userId', data.user.id.toString())
    localStorage.setItem('username', data.user.username)
    localStorage.setItem('isLoggedIn', 'true')
  }

  // 刷新token
  const updateToken = async () => {
    try {
      if (!refreshToken.value) {
        throw new Error('没有刷新令牌')
      }
      
      const response = await apiRefreshToken(refreshToken.value)
      token.value = response.access
      localStorage.setItem('token', response.access)
      return response.access
    } catch (error) {
      // 刷新token失败，清除用户信息
      logout()
      throw error
    }
  }

  // 退出登录
  const logout = () => {
    token.value = ''
    refreshToken.value = ''
    userId.value = null
    username.value = ''
    isLoggedIn.value = false

    // 清除本地存储
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('userId')
    localStorage.removeItem('username')
    localStorage.removeItem('isLoggedIn')
  }

  return {
    token,
    refreshToken,
    userId,
    username,
    isLoggedIn,
    login,
    logout,
    setUserInfo,
    updateToken
  }
}) 