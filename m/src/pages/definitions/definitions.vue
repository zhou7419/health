<template>
  <view class="page-wrap">
    <!-- 新增按钮 -->
    <view class="top-bar card">
      <button class="btn-add" @click="openDialog()">＋ 新增指标</button>
    </view>

    <!-- 定义列表 -->
    <view v-if="loading" class="empty-state">
      <text class="empty-text">加载中...</text>
    </view>

    <view v-else-if="!definitions.length" class="empty-state">
      <text class="empty-icon">📏</text>
      <text class="empty-text">暂无指标定义</text>
    </view>

    <view v-else class="def-list">
      <view v-for="d in definitions" :key="d.id" class="card def-card">
        <view class="flex-between">
          <text class="def-name">{{ d.name }}</text>
          <view class="def-actions">
            <text class="action-link" @click="openDialog(d)">编辑</text>
            <text class="action-link danger" @click="handleDelete(d)">删除</text>
          </view>
        </view>
        <view class="def-meta flex-row">
          <text class="meta-item" v-if="d.unit">单位：{{ d.unit }}</text>
          <text class="meta-item" v-if="d.expected_min != null && d.expected_max != null">
            参考：{{ d.expected_min }} - {{ d.expected_max }}
          </text>
          <text class="meta-item" v-else-if="d.expected_min != null">
            参考：≥ {{ d.expected_min }}
          </text>
          <text class="meta-item" v-else-if="d.expected_max != null">
            参考：≤ {{ d.expected_max }}
          </text>
          <text class="meta-item" v-else>暂无参考范围</text>
        </view>
      </view>
    </view>

    <!-- 新增/编辑弹窗 -->
    <uni-popup ref="dialogPopup" type="center" :mask-click="true">
      <view class="dialog">
        <view class="dialog-header">
          <text class="dialog-title">{{ isEdit ? '编辑指标' : '新增指标' }}</text>
          <text class="dialog-close" @click="closeDialog">✕</text>
        </view>
        <view class="dialog-body">
          <view class="form-row">
            <text class="form-label">名称</text>
            <input class="form-input" v-model="form.name" placeholder="如：体重、收缩压" />
          </view>
          <view class="form-row">
            <text class="form-label">单位</text>
            <input class="form-input" v-model="form.unit" placeholder="如：kg、mmHg" />
          </view>
          <view class="form-row">
            <text class="form-label">参考下限</text>
            <input class="form-input" v-model.number="form.expected_min" type="digit" placeholder="期望最小值" />
          </view>
          <view class="form-row">
            <text class="form-label">参考上限</text>
            <input class="form-input" v-model.number="form.expected_max" type="digit" placeholder="期望最大值" />
          </view>
        </view>
        <view class="dialog-footer">
          <button class="btn-cancel" @click="closeDialog">取消</button>
          <button class="btn-confirm" :loading="submitting" @click="submitDef">保存</button>
        </view>
      </view>
    </uni-popup>
  </view>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '@/api/index.js'
import { checkAuth } from '@/router.js'

const definitions = ref([])
const loading = ref(false)
const submitting = ref(false)
const dialogPopup = ref(null)
const isEdit = ref(false)

const form = reactive({
  id: null,
  name: '',
  unit: '',
  expected_min: undefined,
  expected_max: undefined
})

const fetchDefinitions = async () => {
  loading.value = true
  try {
    definitions.value = await api.get('/definitions/', { limit: 1000 })
  } catch (e) {}
  loading.value = false
}

const openDialog = (def = null) => {
  if (def) {
    isEdit.value = true
    form.id = def.id
    form.name = def.name
    form.unit = def.unit || ''
    form.expected_min = def.expected_min
    form.expected_max = def.expected_max
  } else {
    isEdit.value = false
    form.id = null
    form.name = ''
    form.unit = ''
    form.expected_min = undefined
    form.expected_max = undefined
  }
  dialogPopup.value.open()
}

const closeDialog = () => {
  dialogPopup.value.close()
}

const submitDef = async () => {
  if (!form.name) return uni.showToast({ title: '请输入指标名称', icon: 'none' })
  submitting.value = true
  try {
    const payload = {
      name: form.name,
      unit: form.unit || null,
      expected_min: form.expected_min ?? null,
      expected_max: form.expected_max ?? null
    }
    if (isEdit.value) {
      await api.put(`/definitions/${form.id}`, payload)
      uni.showToast({ title: '更新成功', icon: 'success' })
    } else {
      await api.post('/definitions/', payload)
      uni.showToast({ title: '新增成功', icon: 'success' })
    }
    closeDialog()
    fetchDefinitions()
  } catch (e) {}
  submitting.value = false
}

const handleDelete = (def) => {
  uni.showModal({
    title: '确认删除',
    content: `确定要删除「${def.name}」吗？将级联删除相关记录！`,
    success: async (res) => {
      if (res.confirm) {
        try {
          await api.delete(`/definitions/${def.id}`)
          uni.showToast({ title: '删除成功', icon: 'success' })
          fetchDefinitions()
        } catch (e) {}
      }
    }
  })
}

onMounted(() => {
  checkAuth() && fetchDefinitions()
})
</script>

<style lang="scss" scoped>
.top-bar {
  text-align: center;

  .btn-add {
    width: 100%;
    height: 72rpx;
    line-height: 72rpx;
    background: #409EFF;
    color: #fff;
    font-size: 28rpx;
    border-radius: 12rpx;
    border: none;

    &::after { border: none; }
  }
}

.def-list {
  margin-top: 12rpx;
}

.def-card {
  margin-bottom: 12rpx;

  .def-name {
    font-size: 32rpx;
    font-weight: 600;
    color: #303133;
  }

  .def-actions {
    display: flex;
    gap: 24rpx;

    .action-link {
      font-size: 26rpx;
      color: #409EFF;
      padding: 4rpx;

      &.danger { color: #F56C6C; }
    }
  }

  .def-meta {
    margin-top: 12rpx;

    .meta-item {
      font-size: 24rpx;
      color: #909399;
      background: #f5f7fa;
      padding: 4rpx 12rpx;
      border-radius: 6rpx;
      margin-right: 12rpx;
    }
  }
}

// 弹窗样式与 persons 页面共用 .dialog 结构
.dialog {
  width: 580rpx;
  background: #fff;
  border-radius: 24rpx;
  overflow: hidden;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 32rpx;
  border-bottom: 1rpx solid #f0f0f0;

  .dialog-title {
    font-size: 34rpx;
    font-weight: bold;
  }

  .dialog-close {
    font-size: 32rpx;
    color: #c0c4cc;
    padding: 8rpx;
  }
}

.dialog-body {
  padding: 32rpx;

  .form-row {
    margin-bottom: 24rpx;

    .form-label {
      font-size: 28rpx;
      color: #606266;
      margin-bottom: 12rpx;
      display: block;
    }

    .form-input {
      height: 80rpx;
      background: #f5f7fa;
      border-radius: 12rpx;
      padding: 0 20rpx;
      font-size: 28rpx;
    }
  }
}

.dialog-footer {
  display: flex;
  padding: 20rpx 32rpx 32rpx;
  gap: 20rpx;

  button {
    flex: 1;
    height: 80rpx;
    line-height: 80rpx;
    border-radius: 40rpx;
    font-size: 28rpx;
    border: none;

    &::after { border: none; }
  }

  .btn-cancel {
    background: #f5f7fa;
    color: #606266;
  }

  .btn-confirm {
    background: #409EFF;
    color: #fff;
  }
}
</style>
