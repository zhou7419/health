import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 60000
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (resp) => resp,
  (error) => {
    const status = error?.response?.status
    if (status === 401) {
      localStorage.removeItem('access_token')
      ElMessage.error('请先登录或登录已过期')
      router.push('/login')
    } else if (status === 429) {
      const msg = error.response?.data?.detail || '请求过于频繁'
      ElMessage.error(msg)
    } else {
      console.error('API Error:', error)
    }
    return Promise.reject(error)
  }
)

export default api