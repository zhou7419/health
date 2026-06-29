// 路由配置 - 模拟简版 vue-router（uni-app 使用 pages.json 管理路由）
// 此文件提供导航守卫和路由辅助函数

import { ref } from 'vue'

// 当前路由信息
export const currentRoute = ref({
  path: '',
  query: {}
})

// 路由跳转辅助函数
export const navigateTo = (url, params = {}) => {
  const queryStr = Object.keys(params)
    .map(k => `${k}=${encodeURIComponent(params[k])}`)
    .join('&')
  const fullUrl = queryStr ? `${url}?${queryStr}` : url
  uni.navigateTo({ url: fullUrl })
}

export const redirectTo = (url) => {
  uni.redirectTo({ url })
}

export const switchTab = (url) => {
  uni.switchTab({ url })
}

export const reLaunch = (url) => {
  uni.reLaunch({ url })
}

export const navigateBack = (delta = 1) => {
  uni.navigateBack({ delta })
}

// 路由守卫检查
export const checkAuth = () => {
  const token = uni.getStorageSync('access_token')
  if (!token) {
    reLaunch('/pages/login/login')
    return false
  }
  return true
}

// 登录成功后的跳转
export const onLoginSuccess = () => {
  switchTab('/pages/ledger/ledger')
}

// 退出登录
export const logout = () => {
  uni.removeStorageSync('access_token')
  reLaunch('/pages/login/login')
}
