<template>
  <view class="login-page">
    <view class="login-bg"></view>
    <view class="login-card">
      <view class="login-logo">
        <text class="logo-icon">❤️</text>
        <text class="logo-text">体检指标台账</text>
        <text class="logo-sub">Health Metrics</text>
      </view>

      <view class="form-area">
        <view class="input-group">
          <text class="input-label">用户名</text>
          <input
            class="input-field"
            v-model="form.username"
            placeholder="请输入用户名"
            placeholder-style="color:#c0c4cc"
          />
        </view>

        <view class="input-group">
          <text class="input-label">密码</text>
          <input
            class="input-field"
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            placeholder-style="color:#c0c4cc"
            @confirm="handleLogin"
          />
        </view>

        <button
          class="login-btn"
          :loading="loading"
          :disabled="loading"
          @click="handleLogin"
        >
          {{ loading ? '登录中...' : '登 录' }}
        </button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { reactive, ref } from 'vue'
import api from '@/api/index.js'
import { onLoginSuccess } from '@/router.js'

const loading = ref(false)
const form = reactive({
  username: 'admin',
  password: ''
})

const handleLogin = async () => {
  if (!form.username || !form.password) {
    return uni.showToast({ title: '请输入用户名和密码', icon: 'none' })
  }

  loading.value = true
  try {
    const res = await api.post('/auth/login', {
      username: form.username,
      password: form.password
    })
    uni.setStorageSync('access_token', res.access_token)
    uni.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(() => {
      onLoginSuccess()
    }, 800)
  } catch (e) {
    // 错误已在 api 层处理
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 40rpx;
}

.login-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #409EFF 0%, #66b1ff 40%, #ecf5ff 100%);
  z-index: -1;
}

.login-card {
  width: 100%;
  max-width: 600rpx;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 24rpx;
  padding: 60rpx 48rpx;
  box-shadow: 0 16rpx 48rpx rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(20rpx);
}

.login-logo {
  text-align: center;
  margin-bottom: 60rpx;

  .logo-icon {
    font-size: 72rpx;
    display: block;
    margin-bottom: 16rpx;
  }

  .logo-text {
    font-size: 40rpx;
    font-weight: bold;
    color: #303133;
    display: block;
  }

  .logo-sub {
    font-size: 24rpx;
    color: #909399;
    margin-top: 8rpx;
    display: block;
  }
}

.form-area {
  .input-group {
    margin-bottom: 32rpx;

    .input-label {
      font-size: 28rpx;
      color: #606266;
      margin-bottom: 12rpx;
      display: block;
    }

    .input-field {
      height: 88rpx;
      background: #f5f7fa;
      border-radius: 12rpx;
      padding: 0 24rpx;
      font-size: 30rpx;
      border: 2rpx solid #f5f7fa;
      transition: border-color 0.3s;

      &:focus {
        border-color: #409EFF;
        background: #fff;
      }
    }
  }
}

.login-btn {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  background: linear-gradient(135deg, #409EFF, #66b1ff);
  color: #fff;
  font-size: 32rpx;
  font-weight: bold;
  border-radius: 44rpx;
  border: none;
  margin-top: 48rpx;

  &::after {
    border: none;
  }

  &:active {
    opacity: 0.85;
  }
}
</style>
