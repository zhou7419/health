<template>
  <view class="page-wrap">
    <!-- 选择器 -->
    <view class="card">
      <view class="form-row">
        <text class="form-label">人员</text>
        <picker mode="selector" :range="persons" range-key="name" @change="onPersonChange">
          <view class="picker-val" :class="{ placeholder: !selectedPerson }">
            {{ selectedPerson || '请选择人员' }}
          </view>
        </picker>
      </view>

      <button
        class="btn-generate"
        :loading="generating"
        :disabled="!personId"
        @click="generate"
      >
        🤖 AI 生成专属健康报告
      </button>
    </view>

    <!-- 加载骨架 -->
    <view v-if="generating" class="card">
      <view class="skeleton">
        <view class="skeleton-line" style="width: 60%;"></view>
        <view class="skeleton-line" style="width: 90%;"></view>
        <view class="skeleton-line" style="width: 80%;"></view>
        <view class="skeleton-line" style="width: 70%;"></view>
        <view class="skeleton-line" style="width: 85%;"></view>
        <view class="skeleton-line" style="width: 50%;"></view>
        <view class="skeleton-line" style="width: 75%;"></view>
        <view class="skeleton-line" style="width: 65%;"></view>
      </view>
      <text class="generating-text">AI 医生正在分析您的所有体检指标历史...</text>
    </view>

    <!-- 结果展示 -->
    <view v-if="adviceHtml && !generating" class="card">
      <view class="advice-content">
        <rich-text :nodes="adviceHtml"></rich-text>
      </view>
    </view>

    <!-- 空状态 -->
    <view v-if="!personId && !generating && !adviceHtml" class="empty-state">
      <text class="empty-icon">🏥</text>
      <text class="empty-text">选择人员并点击生成</text>
      <text class="empty-sub">AI 将分析历史指标并给出改善建议</text>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/index.js'
import { checkAuth } from '@/router.js'

const persons = ref([])
const personId = ref('')
const selectedPerson = ref('')
const generating = ref(false)
const adviceHtml = ref('')

const fetchPersons = async () => {
  try {
    persons.value = await api.get('/persons/', { limit: 100 })
  } catch (e) {}
}

const onPersonChange = (e) => {
  const p = persons.value[e.detail.value]
  personId.value = p.id
  selectedPerson.value = p.name
}

const generate = async () => {
  if (!personId.value) return
  generating.value = true
  adviceHtml.value = ''

  uni.showLoading({ title: 'AI 分析中...', mask: true })

  try {
    const res = await api.post('/smart/advice', { person_id: personId.value })
    if (res && res.advice) {
      adviceHtml.value = res.advice
    }
    uni.showToast({ title: '报告生成完毕', icon: 'success' })
  } catch (e) {
    adviceHtml.value = ''
  }

  uni.hideLoading()
  generating.value = false
}

onMounted(() => {
  checkAuth()
  fetchPersons()
})
</script>

<style lang="scss" scoped>
.form-row {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;

  .form-label {
    width: 100rpx;
    font-size: 28rpx;
    color: #606266;
  }

  .picker-val {
    flex: 1;
    font-size: 28rpx;
    padding: 12rpx 16rpx;
    background: #f5f7fa;
    border-radius: 8rpx;

    &.placeholder { color: #c0c4cc; }
  }
}

.btn-generate {
  width: 100%;
  height: 80rpx;
  line-height: 80rpx;
  background: linear-gradient(135deg, #67C23A, #85ce61);
  color: #fff;
  font-size: 28rpx;
  font-weight: bold;
  border-radius: 40rpx;
  border: none;

  &::after { border: none; }
  &:active { opacity: 0.85; }
}

// 骨架屏
.skeleton {
  padding: 20rpx 0;
}

.skeleton-line {
  height: 24rpx;
  background: linear-gradient(90deg, #f0f0f0 25%, #e8e8e8 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  border-radius: 6rpx;
  margin-bottom: 20rpx;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.generating-text {
  text-align: center;
  font-size: 26rpx;
  color: #909399;
  display: block;
  margin-top: 20rpx;
}

// 富文本内容
.advice-content {
  font-size: 28rpx;
  line-height: 1.8;
  color: #303133;

  // rich-text 内部元素样式需要通过内联或全局样式调整
}
</style>
