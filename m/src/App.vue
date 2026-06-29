<template>
  <div id="app-root">
    <router-view />
  </div>
</template>

<script setup>
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'

onLaunch(() => {
  console.log('[Health Metrics] App launched')
  // 检查登录状态
  const token = uni.getStorageSync('access_token')
  if (!token) {
    console.log('[Health Metrics] 未登录，首次启动')
  }
})

onShow(() => {
  console.log('[Health Metrics] App onShow')
})

onHide(() => {
  console.log('[Health Metrics] App onHide')
})
</script>

<style lang="scss">
@import '@/uni.scss';

page {
  background-color: $uni-bg-color;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
    'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial,
    sans-serif;
  font-size: $uni-font-size-base;
  color: $uni-text-color;
  -webkit-font-smoothing: antialiased;
}

// 重置常用样式
view, text, image, scroll-view, input, button {
  box-sizing: border-box;
}

// 卡片样式
.card {
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  margin: 20rpx;
  box-shadow: 0 2rpx 16rpx 0 rgba(0, 0, 0, 0.04);
}

// 页面容器
.page-wrap {
  min-height: 100vh;
  padding-bottom: 40rpx;
}

// 空状态
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 40rpx;
  color: $uni-color-info;

  .empty-icon {
    font-size: 80rpx;
    margin-bottom: 24rpx;
  }

  .empty-text {
    font-size: 28rpx;
    color: #c0c4cc;
  }
}

// 异常值高亮
.val-abnormal {
  color: $uni-color-danger;
  font-weight: bold;
}

.val-normal {
  color: $uni-color-success;
  font-weight: bold;
}

// 工具类
.flex-row {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.text-ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mt-sm { margin-top: $uni-spacing-sm; }
.mt-base { margin-top: $uni-spacing-base; }
.mt-lg { margin-top: $uni-spacing-lg; }
.mb-sm { margin-bottom: $uni-spacing-sm; }
.mb-base { margin-bottom: $uni-spacing-base; }
.mb-lg { margin-bottom: $uni-spacing-lg; }
</style>
