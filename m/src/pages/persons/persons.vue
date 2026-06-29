<template>
  <view class="page-wrap">
    <!-- 新增按钮 -->
    <view class="top-bar card">
      <button class="btn-add-person" @click="openDialog()">
        ＋ 新增人员
      </button>
    </view>

    <!-- 人员列表 -->
    <view v-if="loading" class="empty-state">
      <text class="empty-text">加载中...</text>
    </view>

    <view v-else-if="!persons.length" class="empty-state">
      <text class="empty-icon">👥</text>
      <text class="empty-text">暂无人员</text>
    </view>

    <view v-else class="person-list">
      <view v-for="p in persons" :key="p.id" class="card person-card flex-between">
        <view>
          <text class="person-name">{{ p.name }}</text>
          <text class="person-gender" v-if="p.gender"> · {{ p.gender }}</text>
          <text class="person-meta">创建于 {{ p.created_at?.split('T')[0] || '-' }}</text>
        </view>
        <button class="btn-delete" @click="handleDelete(p)">
          🗑
        </button>
      </view>
    </view>

    <!-- 新增弹窗 -->
    <uni-popup ref="dialogPopup" type="center" :mask-click="true">
      <view class="dialog">
        <view class="dialog-header">
          <text class="dialog-title">新增人员</text>
          <text class="dialog-close" @click="closeDialog">✕</text>
        </view>
        <view class="dialog-body">
          <view class="form-row">
            <text class="form-label">姓名</text>
            <input class="form-input" v-model="form.name" placeholder="请输入姓名" />
          </view>
          <view class="form-row">
            <text class="form-label">性别</text>
            <view class="gender-group">
              <view
                v-for="g in ['男', '女', '其他']"
                :key="g"
                :class="['gender-tag', { active: form.gender === g }]"
                @click="form.gender = g"
              >
                {{ g }}
              </view>
            </view>
          </view>
        </view>
        <view class="dialog-footer">
          <button class="btn-cancel" @click="closeDialog">取消</button>
          <button class="btn-confirm" :loading="submitting" @click="submitPerson">保存</button>
        </view>
      </view>
    </uni-popup>
  </view>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '@/api/index.js'
import { checkAuth } from '@/router.js'

const persons = ref([])
const loading = ref(false)
const submitting = ref(false)
const dialogPopup = ref(null)
const form = reactive({ name: '', gender: '' })

const fetchPersons = async () => {
  loading.value = true
  try {
    persons.value = await api.get('/persons/', { limit: 100 })
  } catch (e) {}
  loading.value = false
}

const openDialog = () => {
  form.name = ''
  form.gender = ''
  dialogPopup.value.open()
}

const closeDialog = () => {
  dialogPopup.value.close()
}

const submitPerson = async () => {
  if (!form.name) return uni.showToast({ title: '请输入姓名', icon: 'none' })
  submitting.value = true
  try {
    await api.post('/persons/', { name: form.name, gender: form.gender || null })
    uni.showToast({ title: '新增成功', icon: 'success' })
    closeDialog()
    fetchPersons()
  } catch (e) {}
  submitting.value = false
}

const handleDelete = (p) => {
  uni.showModal({
    title: '确认删除',
    content: `确定要删除「${p.name}」吗？其所有体检记录将被清空！`,
    success: async (res) => {
      if (res.confirm) {
        try {
          await api.delete(`/persons/${p.id}`)
          uni.showToast({ title: '删除成功', icon: 'success' })
          fetchPersons()
        } catch (e) {}
      }
    }
  })
}

onMounted(() => {
  checkAuth() && fetchPersons()
})
</script>

<style lang="scss" scoped>
.top-bar {
  text-align: center;

  .btn-add-person {
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

.person-list {
  margin-top: 12rpx;
}

.person-card {
  margin-bottom: 12rpx;

  .person-name {
    font-size: 32rpx;
    font-weight: 600;
    color: #303133;
  }

  .person-gender {
    font-size: 26rpx;
    color: #909399;
  }

  .person-meta {
    font-size: 22rpx;
    color: #c0c4cc;
    display: block;
    margin-top: 4rpx;
  }

  .btn-delete {
    background: transparent;
    border: none;
    font-size: 36rpx;
    padding: 8rpx;

    &::after { border: none; }
  }
}

// 弹窗
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

    .gender-group {
      display: flex;
      gap: 16rpx;

      .gender-tag {
        flex: 1;
        text-align: center;
        padding: 16rpx 0;
        background: #f5f7fa;
        border-radius: 12rpx;
        font-size: 28rpx;
        color: #606266;

        &.active {
          background: #ecf5ff;
          color: #409EFF;
          font-weight: bold;
        }
      }
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
