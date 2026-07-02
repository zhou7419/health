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

    <!-- 正在生成 - 骨架屏 -->
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

    <!-- 当前结果展示 -->
    <view v-if="currentAdvice && !generating" class="card">
      <view class="advice-header flex-between">
        <text class="advice-date">生成于 {{ currentAdvice.created_at?.split('T')[0] || '刚刚' }}</text>
        <text v-if="currentAdvice.summary" class="advice-summary-tag">{{ currentAdvice.summary }}</text>
      </view>
      <view class="advice-content">
        <rich-text :nodes="currentAdvice.content"></rich-text>
      </view>
    </view>

    <!-- 历史报告列表 -->
    <view class="card" v-if="adviceList.length">
      <view class="section-title flex-between">
        <text>📜 历史报告</text>
        <text class="count-tag">共 {{ adviceList.length }} 条</text>
      </view>

      <view
        v-for="a in adviceList"
        :key="a.id"
        :class="['history-item', { active: currentAdvice?.id === a.id }]"
        @click="viewAdvice(a)"
      >
        <view class="history-info">
          <text class="history-date">{{ a.created_at?.split('T')[0] || '-' }}</text>
          <text class="history-summary" v-if="a.summary">· {{ a.summary }}</text>
        </view>
        <view class="history-actions">
          <text class="action-link danger" @click.stop="handleDelete(a)">删除</text>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view v-if="!personId && !generating && !currentAdvice && !adviceList.length" class="empty-state">
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
const currentAdvice = ref(null)
const adviceList = ref([])

const fetchPersons = async () => {
  try {
    persons.value = await api.get('/persons/', { limit: 100 })
  } catch (e) {}
}

const fetchAdviceHistory = async () => {
  if (!personId.value) return
  try {
    const res = await api.get('/advices/', { person_id: personId.value, page: 1, page_size: 50 })
    adviceList.value = res?.items || []
  } catch (e) {
    adviceList.value = []
  }
}

const onPersonChange = (e) => {
  const p = persons.value[e.detail.value]
  personId.value = p.id
  selectedPerson.value = p.name
  currentAdvice.value = null
  fetchAdviceHistory()
}

const generate = async () => {
  if (!personId.value) return
  generating.value = true
  currentAdvice.value = null

  uni.showLoading({ title: 'AI 分析中...', mask: true })

  try {
    const res = await api.post('/smart/advice', { person_id: personId.value })
    if (res && res.advice) {
      // 先展示
      currentAdvice.value = {
        id: null,
        content: res.advice,
        created_at: new Date().toISOString(),
        summary: ''
      }

      // 自动保存到后端
      try {
        const saved = await api.post('/advices/', {
          person_id: personId.value,
          content: res.advice,
          summary: ''
        })
        if (saved && saved.id) {
          currentAdvice.value.id = saved.id
          currentAdvice.value.created_at = saved.created_at
          currentAdvice.value.summary = saved.summary
        }
        // 刷新历史列表
        await fetchAdviceHistory()
      } catch (saveErr) {
        // 保存失败不影响显示
        console.error('save advice error', saveErr)
      }

      uni.showToast({ title: '报告生成完毕', icon: 'success' })
    }
  } catch (e) {
    currentAdvice.value = null
  }

  uni.hideLoading()
  generating.value = false
}

const viewAdvice = (item) => {
  currentAdvice.value = item
  uni.pageScrollTo({ scrollTop: 0, duration: 300 })
}

const handleDelete = (item) => {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除这份健康报告吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await api.delete(`/advices/${item.id}`)
          uni.showToast({ title: '删除成功', icon: 'success' })
          adviceList.value = adviceList.value.filter(a => a.id !== item.id)
          if (currentAdvice.value?.id === item.id) {
            currentAdvice.value = null
          }
        } catch (e) {}
      }
    }
  })
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

// 当前报告
.advice-header {
  margin-bottom: 16rpx;
  padding-bottom: 12rpx;
  border-bottom: 1rpx solid #f0f0f0;

  .advice-date {
    font-size: 22rpx;
    color: #909399;
  }

  .advice-summary-tag {
    font-size: 20rpx;
    color: #E6A23C;
    background: #fdf6ec;
    padding: 2rpx 12rpx;
    border-radius: 20rpx;
  }
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
}

// 历史报告
.section-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #303133;
  margin-bottom: 20rpx;
}

.count-tag {
  font-size: 22rpx;
  color: #909399;
  background: #f5f7fa;
  padding: 4rpx 16rpx;
  border-radius: 20rpx;
}

.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 16rpx;
  border-radius: 12rpx;
  margin-bottom: 8rpx;
  background: #fafafa;

  &.active {
    background: #ecf5ff;
    border: 1rpx solid #d9ecff;
  }

  .history-info {
    flex: 1;
    display: flex;
    align-items: center;
    min-width: 0;

    .history-date {
      font-size: 26rpx;
      color: #303133;
      font-weight: 500;
      flex-shrink: 0;
    }

    .history-summary {
      font-size: 24rpx;
      color: #909399;
      margin-left: 8rpx;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }

  .history-actions {
    flex-shrink: 0;
    margin-left: 12rpx;

    .action-link {
      font-size: 24rpx;
      color: #409EFF;
      padding: 8rpx;

      &.danger { color: #F56C6C; }
    }
  }
}
</style>
