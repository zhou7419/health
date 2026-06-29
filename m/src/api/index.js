// API 封装 - 基于 uni.request

// 运行环境检测：H5 开发模式走 Vite 代理，App/生产模式直连后端
const isH5Dev = typeof window !== 'undefined' && window.location.protocol === 'http:' && window.location.hostname === 'localhost'
const API_HOST = isH5Dev ? '' : 'http://129.28.118.227:8002'
const BASE_URL = API_HOST + '/api/v1'

// 请求拦截器
const request = (options) => {
  const token = uni.getStorageSync('access_token')

  return new Promise((resolve, reject) => {
    uni.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Authorization': token ? `Bearer ${token}` : '',
        ...(options.header || {})
      },
      timeout: options.timeout || 30000,
      success: (res) => {
        if (res.statusCode === 401) {
          uni.removeStorageSync('access_token')
          uni.showToast({ title: '请重新登录', icon: 'none' })
          // 跳转到登录页
          const pages = getCurrentPages()
          const currentPage = pages[pages.length - 1]
          if (currentPage && currentPage.route !== 'pages/login/login') {
            setTimeout(() => {
              uni.reLaunch({ url: '/pages/login/login' })
            }, 1500)
          }
          reject(res)
        } else if (res.statusCode === 429) {
          uni.showToast({ title: '操作过于频繁，请稍后再试', icon: 'none' })
          reject(res)
        } else if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          const msg = res.data?.detail || '请求失败'
          uni.showToast({ title: msg, icon: 'none' })
          reject(res)
        }
      },
      fail: (err) => {
        uni.showToast({ title: '网络请求失败', icon: 'none' })
        reject(err)
      }
    })
  })
}

// 文件上传
const uploadFile = (options) => {
  const token = uni.getStorageSync('access_token')

  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: BASE_URL + options.url,
      filePath: options.filePath,
      name: options.name || 'file',
      formData: options.formData || {},
      header: {
        'Authorization': token ? `Bearer ${token}` : '',
        ...(options.header || {})
      },
      timeout: options.timeout || 60000,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try {
            resolve(JSON.parse(res.data))
          } catch {
            resolve(res.data)
          }
        } else if (res.statusCode === 401) {
          uni.removeStorageSync('access_token')
          uni.showToast({ title: '请重新登录', icon: 'none' })
          reject(res)
        } else {
          let detail = '上传失败'
          try {
            detail = JSON.parse(res.data)?.detail || detail
          } catch {}
          uni.showToast({ title: detail, icon: 'none' })
          reject(res)
        }
      },
      fail: (err) => {
        uni.showToast({ title: '上传失败', icon: 'none' })
        reject(err)
      }
    })
  })
}

// 便捷方法
const api = {
  get: (url, data) => request({ url, method: 'GET', data }),
  post: (url, data) => request({ url, method: 'POST', data }),
  put: (url, data) => request({ url, method: 'PUT', data }),
  delete: (url, data) => request({ url, method: 'DELETE', data }),
  upload: (url, filePath, formData, name) => uploadFile({ url, filePath, formData, name }),
  uploadFiles: (url, files, formData) => {
    // 多文件上传 - 小程序环境下需要逐个上传
    const uploads = files.map(file => uploadFile({ url, filePath: file, name: 'files', formData }))
    return Promise.all(uploads)
  }
}

export default api
