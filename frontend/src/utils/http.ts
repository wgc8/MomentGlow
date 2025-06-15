import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'

// 创建axios实例
const http: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 15000
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
      const userStore = useUserStore()
      userStore.logout()
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
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
http.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data
  },
  error => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // 未授权，尝试刷新token
          if (!error.config._retry) {
            return handleTokenExpired(error.config)
          }
          // 如果已经尝试过刷新token，则清除用户信息并跳转到登录页
          const userStore = useUserStore()
          userStore.logout()
          window.location.href = '/login'
          break
        case 403:
          ElMessage.error('没有权限访问该资源')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        default:
          ElMessage.error(error.response.data.message || '请求失败')
      }
    } else {
      ElMessage.error('网络错误，请检查您的网络连接')
    }
    
    return Promise.reject(error)
  }
)

// 封装请求方法
const request = {
  get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return http.get(url, config)
  },
  
  post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return http.post(url, data, config)
  },
  
  put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return http.put(url, data, config)
  },
  
  delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return http.delete(url, config)
  }
}

export default request 