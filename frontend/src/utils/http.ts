import axios from 'axios'
import { useUserStore } from '@/store/user'

// 创建axios实例
const http = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000
})

// 是否正在刷新token
let isRefreshing = false
// 重试队列，每一项将是一个待执行的函数形式
let requests: Array<(token: string) => void> = []

/**
 * 处理token过期
 * @param config 原始请求配置
 * @returns 返回带有新token的请求Promise
 */
const handleTokenExpired = async (config: any) => {
  // 标记该请求已经尝试过重试
  config._retry = true
  
  // 如果当前没有在刷新token
  if (!isRefreshing) {
    isRefreshing = true
    
    try {
      // 尝试刷新token
      const userStore = useUserStore()
      const newToken = await userStore.updateToken()
      
      // 更新队列中所有请求的token
      requests.forEach(cb => cb(newToken))
      // 清空队列
      requests = []
      
      // 重新发起原请求
      config.headers.Authorization = `Bearer ${newToken}`
      return http(config)
    } catch (refreshError) {
      // 刷新token失败，清除用户信息并跳转到登录页
      window.location.href = '/login'
      return Promise.reject(refreshError)
    } finally {
      isRefreshing = false
    }
  } else {
    // 如果已经在刷新token，将请求加入队列
    return new Promise(resolve => {
      requests.push((token: string) => {
        config.headers.Authorization = `Bearer ${token}`
        resolve(http(config))
      })
    })
  }
}

// 请求拦截器
http.interceptors.request.use(
  config => {
    // 从本地存储获取token
    const token = localStorage.getItem('token')
    // 如果token存在，添加到请求头
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
http.interceptors.response.use(
  response => {
    return response
  },
  async error => {
    if (!error.response) {
      return Promise.reject(error)
    }

    const { status } = error.response
    const originalRequest = error.config

    // token过期处理 (状态码401表示未授权)
    if (status === 401 && !originalRequest._retry) {
      return handleTokenExpired(originalRequest)
    }
    
    return Promise.reject(error)
  }
)

export default http 