<template>
  <view class="page-wrap">
    <!-- 筛选栏 -->
    <view class="filter-bar">
      <picker
        class="filter-item"
        mode="selector"
        :range="personOptions"
        range-key="name"
        @change="onPersonFilter"
      >
        <view class="picker-content">
          <text class="picker-label">{{ filterPersonName || '全部人员' }}</text>
          <text class="picker-arrow">▼</text>
        </view>
      </picker>

      <picker
        class="filter-item"
        mode="date"
        :value="filterDate"
        @change="onDateFilter"
      >
        <view class="picker-content">
          <text class="picker-label">{{ filterDate || '选择日期' }}</text>
          <text class="picker-arrow">📅</text>
        </view>
      </picker>

      <picker
        class="filter-item"
        mode="selector"
        :range="metricOptions"
        range-key="name"
        @change="onMetricFilter"
      >
        <view class="picker-content">
          <text class="picker-label">{{ filterMetricName || '全部指标' }}</text>
          <text class="picker-arrow">▼</text>
        </view>
      </picker>
    </view>

    <!-- 快捷操作 -->
    <view class="action-row" v-if="filterDate">
      <button class="btn-danger-sm" @click="handleDeleteByDate">
        删除「{{ filterDate }}」记录
      </button>
    </view>

    <!-- 记录列表 -->
    <view v-if="loading" class="loading-wrap">
      <text class="loading-text">加载中...</text>
    </view>

    <view v-else-if="records.length === 0" class="empty-state">
      <text class="empty-icon">📋</text>
      <text class="empty-text">暂无体检记录</text>
      <text class="empty-sub">点击底部「录入」开始添加数据</text>
    </view>

    <view v-else class="record-list">
      <view
        v-for="item in records"
        :key="item.id"
        class="card record-card"
      >
        <view class="record-header flex-between">
          <view class="flex-row">
            <text class="record-date">{{ item.record_date }}</text>
            <text class="record-person">{{ item.person.name }}</text>
          </view>
          <view class="record-actions">
            <text class="action-link" @click="handleEdit(item)">编辑</text>
            <text class="action-link danger" @click="handleDelete(item)">删除</text>
          </view>
        </view>

        <view class="record-body flex-between">
          <view class="flex-row">
            <text class="metric-name">{{ item.metric.name }}</text>
          </view>
          <view class="flex-row">
            <text :class="['metric-value', getValueClass(item.value, item.metric)]">
              {{ item.value }}
            </text>
            <text class="metric-unit" v-if="item.metric.unit">{{ item.metric.unit }}</text>
          </view>
        </view>

        <view class="record-footer flex-between" v-if="item.metric.expected_min != null || item.metric.expected_max != null">
          <text class="range-label">参考范围</text>
          <text class="range-value">{{ formatRange(item.metric) }}</text>
        </view>

        <view class="record-note" v-if="item.notes">
          <text class="note-text">📝 {{ item.notes }}</text>
        </view>
      </view>

      <!-- 加载更多 -->
      <view v-if="hasMore" class="load-more" @click="loadMore">
        <text>加载更多...</text>
      </view>
    </view>

    <!-- 编辑弹窗 -->
    <uni-popup ref="editPopup" type="bottom" :mask-click="true">
      <view class="popup-wrap">
        <view class="popup-header flex-between">
          <text class="popup-title">编辑体检记录</text>
          <text class="popup-close" @click="closeEdit">✕</text>
        </view>

        <view class="popup-body" v-if="editForm">
          <view class="form-row">
            <text class="form-label">人员</text>
            <text class="form-static">{{ editForm.person_name }}</text>
          </view>
          <view class="form-row">
            <text class="form-label">指标</text>
            <text class="form-static">{{ editForm.metric_name }}</text>
          </view>
          <view class="form-row">
            <text class="form-label">体检日期</text>
            <picker mode="date" :value="editForm.record_date" @change="onEditDateChange">
              <text class="form-picker-value">{{ editForm.record_date || '请选择' }}</text>
            </picker>
          </view>
          <view class="form-row">
            <text class="form-label">数值</text>
            <input
              class="form-input"
              v-model.number="editForm.value"
              type="digit"
              placeholder="请输入数值"
            />
          </view>
          <view class="form-row">
            <text class="form-label">备注</text>
            <input
              class="form-input"
              v-model="editForm.notes"
              placeholder="备注信息（可选）"
            />
          </view>
        </view>

        <view class="popup-footer">
          <button class="btn-confirm" :loading="submitting" @click="submitEdit">保存</button>
        </view>
      </view>
    </uni-popup>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api/index.js'
import { formatRange, isValueNormal } from '@/utils/index.js'
import { checkAuth } from '@/router.js'

const records = ref([])
const persons = ref([])
const definitions = ref([])
const loading = ref(false)
const submitting = ref(false)
const hasMore = ref(false)

const filterDate = ref('')
const filterPersonName = ref('')
const filterMetricName = ref('')
const filterPersonId = ref('')
const filterMetricId = ref('')
const currentPage = ref(0)

// 编辑表单
const editForm = ref(null)
const editPopup = ref(null)

const personOptions = computed(() => [
  { id: '', name: '全部人员' },
  ...persons.value
])

const metricOptions = computed(() => [
  { id: '', name: '全部指标' },
  ...definitions.value
])

// 数据加载
const fetchRecords = async (append = false) => {
  loading.value = true
  const skip = append ? (currentPage.value + 1) * 20 : 0
  try {
    let params = { limit: 20, skip }
    if (filterPersonId.value) params.person_id = filterPersonId.value
    if (filterMetricId.value) params.metric_id = filterMetricId.value
    if (filterDate.value) params.record_date = filterDate.value

    const res = await api.get('/metrics/', params)
    if (append) {
      records.value.push(...res)
    } else {
      records.value = res
    }
    hasMore.value = res.length >= 20
    currentPage.value = append ? currentPage.value + 1 : 0
  } catch (e) {
    if (!append) records.value = []
  } finally {
    loading.value = false
    uni.stopPullDownRefresh()
  }
}

const loadMore = () => fetchRecords(true)

const fetchPersons = async () => {
  try {
    persons.value = await api.get('/persons/', { limit: 100 })
  } catch (e) {}
}

const fetchDefinitions = async () => {
  try {
    definitions.value = await api.get('/definitions/', { limit: 1000 })
  } catch (e) {}
}

// 筛选
const onPersonFilter = (e) => {
  const item = personOptions.value[e.detail.value]
  filterPersonName.value = item.id ? item.name : ''
  filterPersonId.value = item.id || ''
  fetchRecords()
}

const onDateFilter = (e) => {
  filterDate.value = e.detail.value
  fetchRecords()
}

const onMetricFilter = (e) => {
  const item = metricOptions.value[e.detail.value]
  filterMetricName.value = item.id ? item.name : ''
  filterMetricId.value = item.id || ''
  fetchRecords()
}

// 判断值样式
const getValueClass = (value, metric) => {
  const normal = isValueNormal(value, metric)
  if (normal === null) return ''
  return normal ? 'val-normal' : 'val-abnormal'
}

// 编辑
const handleEdit = (item) => {
  editForm.value = {
    id: item.id,
    person_name: item.person.name,
    metric_name: item.metric.name,
    record_date: item.record_date,
    value: item.value,
    notes: item.notes || ''
  }
  editPopup.value.open()
}

const onEditDateChange = (e) => {
  if (editForm.value) {
    editForm.value.record_date = e.detail.value
  }
}

const closeEdit = () => {
  editPopup.value.close()
  editForm.value = null
}

const submitEdit = async () => {
  if (!editForm.value || editForm.value.value === '' || editForm.value.value === null) {
    return uni.showToast({ title: '请输入数值', icon: 'none' })
  }
  submitting.value = true
  try {
    await api.put(`/metrics/${editForm.value.id}`, {
      value: Number(editForm.value.value),
      record_date: editForm.value.record_date,
      notes: editForm.value.notes
    })
    uni.showToast({ title: '更新成功', icon: 'success' })
    closeEdit()
    fetchRecords()
  } catch (e) {}
  submitting.value = false
}

// 删除
const handleDelete = (item) => {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除这条体检记录吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await api.delete(`/metrics/${item.id}`)
          uni.showToast({ title: '删除成功', icon: 'success' })
          fetchRecords()
        } catch (e) {}
      }
    }
  })
}

const handleDeleteByDate = () => {
  if (!filterDate.value) return
  uni.showModal({
    title: '批量删除',
    content: `确定要删除「${filterDate.value}」的所有体检记录吗？`,
    success: async (res) => {
      if (res.confirm) {
        try {
          let url = `/metrics/date/${filterDate.value}`
          if (filterPersonId.value) {
            url += `?person_id=${filterPersonId.value}`
          }
          const result = await api.delete(url)
          uni.showToast({
            title: `已删除 ${result.deleted_count} 条记录`,
            icon: 'success'
          })
          filterDate.value = ''
          fetchRecords()
        } catch (e) {}
      }
    }
  })
}

// 下拉刷新
onMounted(() => {
  checkAuth() && fetchRecords()
  fetchPersons()
  fetchDefinitions()
})
</script>

<style lang="scss" scoped>
.filter-bar {
  display: flex;
  padding: 20rpx;
  background: #fff;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
  gap: 12rpx;
  position: sticky;
  top: 0;
  z-index: 10;

  .filter-item {
    flex: 1;

    .picker-content {
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: #f5f7fa;
      border-radius: 8rpx;
      padding: 12rpx 16rpx;
      font-size: 26rpx;

      .picker-arrow {
        font-size: 20rpx;
        color: #c0c4cc;
      }
    }
  }
}

.action-row {
  padding: 12rpx 20rpx 0;
  text-align: right;

  .btn-danger-sm {
    display: inline-block;
    font-size: 24rpx;
    color: #F56C6C;
    background: #fef0f0;
    border: 1rpx solid #fde2e2;
    border-radius: 6rpx;
    padding: 8rpx 20rpx;
    line-height: 1.4;

    &::after { border: none; }
  }
}

.loading-wrap {
  text-align: center;
  padding: 100rpx;
  color: #909399;
}

.record-list {
  padding: 0 0 40rpx;
}

.record-card {
  .record-header {
    margin-bottom: 16rpx;

    .record-date {
      font-size: 24rpx;
      color: #909399;
      background: #f5f7fa;
      padding: 4rpx 12rpx;
      border-radius: 6rpx;
      margin-right: 16rpx;
    }

    .record-person {
      font-size: 24rpx;
      color: #606266;
      font-weight: 500;
    }

    .record-actions {
      display: flex;
      gap: 20rpx;

      .action-link {
        font-size: 24rpx;
        color: #409EFF;
        padding: 4rpx 8rpx;

        &.danger { color: #F56C6C; }
      }
    }
  }

  .record-body {
    margin-bottom: 12rpx;

    .metric-name {
      font-size: 30rpx;
      font-weight: 600;
      color: #303133;
    }

    .metric-value {
      font-size: 36rpx;
      font-weight: bold;
      margin-right: 8rpx;
    }

    .metric-unit {
      font-size: 24rpx;
      color: #909399;
    }
  }

  .record-footer {
    padding-top: 12rpx;
    border-top: 1rpx solid #f0f0f0;

    .range-label {
      font-size: 22rpx;
      color: #c0c4cc;
    }

    .range-value {
      font-size: 24rpx;
      color: #606266;
    }
  }

  .record-note {
    margin-top: 12rpx;
    .note-text {
      font-size: 24rpx;
      color: #909399;
    }
  }
}

.load-more {
  text-align: center;
  padding: 30rpx;
  color: #409EFF;
  font-size: 26rpx;
}

// 弹窗样式
.popup-wrap {
  background: #fff;
  border-radius: 24rpx 24rpx 0 0;
  padding: 32rpx 32rpx 60rpx;
  max-height: 70vh;
  overflow-y: auto;
}

.popup-header {
  margin-bottom: 32rpx;

  .popup-title {
    font-size: 34rpx;
    font-weight: bold;
  }

  .popup-close {
    font-size: 36rpx;
    color: #c0c4cc;
    padding: 8rpx;
  }
}

.popup-body {
  .form-row {
    display: flex;
    align-items: center;
    margin-bottom: 24rpx;

    .form-label {
      width: 140rpx;
      font-size: 28rpx;
      color: #606266;
      flex-shrink: 0;
    }

    .form-static {
      font-size: 28rpx;
      color: #303133;
    }

    .form-input {
      flex: 1;
      height: 72rpx;
      background: #f5f7fa;
      border-radius: 8rpx;
      padding: 0 16rpx;
      font-size: 28rpx;
    }

    .form-picker-value {
      font-size: 28rpx;
      color: #409EFF;
    }
  }
}

.popup-footer {
  margin-top: 32rpx;

  .btn-confirm {
    width: 100%;
    height: 80rpx;
    line-height: 80rpx;
    background: #409EFF;
    color: #fff;
    font-size: 30rpx;
    border-radius: 40rpx;
    border: none;

    &::after { border: none; }
  }
}
</style>
