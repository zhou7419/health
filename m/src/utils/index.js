/**
 * 工具函数
 */

// 格式化日期
export const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 获取今天日期字符串
export const getToday = () => {
  const d = new Date()
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 格式化期望区间显示
export const formatRange = (metric) => {
  if (metric.expected_min != null && metric.expected_max != null) {
    return `${metric.expected_min} - ${metric.expected_max}`
  }
  if (metric.expected_min != null) return `≥ ${metric.expected_min}`
  if (metric.expected_max != null) return `≤ ${metric.expected_max}`
  return '-'
}

// 判断数值是否在正常范围内
export const isValueNormal = (value, metric) => {
  if (metric.expected_min != null && value < metric.expected_min) return false
  if (metric.expected_max != null && value > metric.expected_max) return false
  if (metric.expected_min == null && metric.expected_max == null) return null // 无参考范围
  return true
}

// 防抖
export const debounce = (fn, delay = 300) => {
  let timer = null
  return function (...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => fn.apply(this, args), delay)
    timer = null
  }
}

// Toast 提示
export const toast = {
  success: (msg) => uni.showToast({ title: msg, icon: 'success' }),
  error: (msg) => uni.showToast({ title: msg, icon: 'error' }),
  warning: (msg) => uni.showToast({ title: msg, icon: 'none' }),
  loading: (msg = '加载中...') => uni.showLoading({ title: msg, mask: true }),
  hide: () => uni.hideLoading()
}
