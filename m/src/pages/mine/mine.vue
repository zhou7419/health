<template>
  <view class="page-wrap">
    <!-- 用户信息区 -->
    <view class="user-card card">
      <view class="user-avatar">👤</view>
      <view class="user-info">
        <text class="user-name">{{ username || 'admin' }}</text>
        <text class="user-role">管理员</text>
      </view>
    </view>

    <!-- 功能菜单 -->
    <view class="menu-section">
      <view class="card menu-item" @click="navigateTo('/pages/persons/persons')">
        <view class="flex-row">
          <text class="menu-icon">👥</text>
          <view class="menu-body">
            <text class="menu-title">人员管理</text>
            <text class="menu-desc">管理系统中的体检人员</text>
          </view>
        </view>
        <text class="menu-arrow">›</text>
      </view>

      <view class="card menu-item" @click="navigateTo('/pages/definitions/definitions')">
        <view class="flex-row">
          <text class="menu-icon">📏</text>
          <view class="menu-body">
            <text class="menu-title">指标字典</text>
            <text class="menu-desc">管理体检指标及参考范围</text>
          </view>
        </view>
        <text class="menu-arrow">›</text>
      </view>

      <view class="card menu-item" @click="navigateTo('/pages/analysis/analysis')">
        <view class="flex-row">
          <text class="menu-icon">📈</text>
          <view class="menu-body">
            <text class="menu-title">趋势分析</text>
            <text class="menu-desc">查看指标历史变化趋势</text>
          </view>
        </view>
        <text class="menu-arrow">›</text>
      </view>

      <view class="card menu-item" @click="navigateTo('/pages/advice/advice')">
        <view class="flex-row">
          <text class="menu-icon">🏥</text>
          <view class="menu-body">
            <text class="menu-title">健康建议</text>
            <text class="menu-desc">AI 生成专属健康报告</text>
          </view>
        </view>
        <text class="menu-arrow">›</text>
      </view>
    </view>

    <!-- 退出登录 -->
    <view class="logout-area">
      <button class="btn-logout" @click="handleLogout">退出登录</button>
    </view>

    <view class="app-version">
      <text>体检指标台账 v1.0.0</text>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/index.js'
import { logout } from '@/router.js'

const username = ref('')

const navigateTo = (url) => {
  uni.navigateTo({ url })
}

const handleLogout = () => {
  uni.showModal({
    title: '确认退出',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) logout()
    }
  })
}

onMounted(async () => {
  try {
    const res = await api.get('/auth/me')
    username.value = (res && res.username) || 'admin'
  } catch (e) {
    username.value = 'admin'
  }
})
</script>

<style lang="scss" scoped>
.user-card {
  display: flex;
  align-items: center;
  padding: 40rpx;
  margin-top: 20rpx;

  .user-avatar {
    width: 100rpx;
    height: 100rpx;
    background: linear-gradient(135deg, #409EFF, #66b1ff);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 50rpx;
    margin-right: 24rpx;
    flex-shrink: 0;
  }

  .user-info {
    .user-name {
      font-size: 36rpx;
      font-weight: bold;
      color: #303133;
      display: block;
    }

    .user-role {
      font-size: 24rpx;
      color: #909399;
      margin-top: 4rpx;
      display: block;
    }
  }
}

.menu-section {
  margin-top: 20rpx;
}

.menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 28rpx;
  margin-bottom: 12rpx;

  .menu-icon {
    font-size: 40rpx;
    margin-right: 20rpx;
    flex-shrink: 0;
  }

  .menu-body {
    .menu-title {
      font-size: 30rpx;
      color: #303133;
      display: block;
    }

    .menu-desc {
      font-size: 24rpx;
      color: #c0c4cc;
      margin-top: 4rpx;
      display: block;
    }
  }

  .menu-arrow {
    font-size: 36rpx;
    color: #c0c4cc;
    flex-shrink: 0;
  }
}

.logout-area {
  margin-top: 60rpx;
  padding: 0 20rpx;

  .btn-logout {
    width: 100%;
    height: 88rpx;
    line-height: 88rpx;
    background: #fff;
    color: #F56C6C;
    font-size: 30rpx;
    border-radius: 16rpx;
    border: 2rpx solid #fde2e2;

    &::after { border: none; }
  }
}

.app-version {
  text-align: center;
  margin-top: 40rpx;
  font-size: 24rpx;
  color: #dcdfe6;
}
</style>
