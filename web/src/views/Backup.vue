<template>
  <div class="page-container">
    <div class="toolbar"><h3>数据库备份与恢复</h3></div>

    <el-alert title="此页面仅管理员可见" type="warning" :closable="false" show-icon style="margin-bottom: 16px;" />

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>下载备份</template>
          <p style="color: #606266; margin-bottom: 16px;">将当前数据库文件下载到本地，作为安全备份。</p>
          <el-button type="primary" @click="handleBackup" :loading="backingUp">
            下载备份文件
          </el-button>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>恢复数据</template>
          <p style="color: #606266; margin-bottom: 16px;">上传之前备份的 <code>.db</code> 文件来恢复数据。当前数据库会自动备份为 <code>.bak</code> 文件。</p>
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            accept=".db"
            :limit="1"
            :on-change="onFileChange"
          >
            <template #trigger>
              <el-button type="primary">选择文件</el-button>
            </template>
            <el-button style="margin-left: 12px;" type="danger" @click="handleRestore" :loading="restoring" :disabled="!selectedFile">
              恢复
            </el-button>
            <template #tip>
              <div class="el-upload__tip">仅支持 .db 文件</div>
            </template>
          </el-upload>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../utils/api'

const backingUp = ref(false)
const restoring = ref(false)
const selectedFile = ref(null)

const handleBackup = async () => {
  backingUp.value = true
  try {
    const res = await api.get('/stats/backup', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = `health-backup-${new Date().toISOString().split('T')[0]}.db`
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('备份下载成功')
  } catch (e) {
    ElMessage.error('备份下载失败')
  } finally {
    backingUp.value = false
  }
}

const onFileChange = (file) => {
  selectedFile.value = file.raw
}

const handleRestore = async () => {
  if (!selectedFile.value) return

  try {
    await ElMessageBox.confirm(
      '恢复数据将替换当前所有数据，确定要继续吗？当前数据库会自动备份。',
      '确认恢复',
      { confirmButtonText: '确定恢复', cancelButtonText: '取消', type: 'warning' }
    )
  } catch {
    return
  }

  restoring.value = true
  try {
    const form = new FormData()
    form.append('file', selectedFile.value)
    await api.post('/stats/restore', form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    ElMessage.success('数据恢复成功，请刷新页面')
  } catch (e) {
    const msg = e.response?.data?.detail || '恢复失败'
    ElMessage.error(msg)
  } finally {
    restoring.value = false
  }
}
</script>

<style scoped>
.page-container { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05); min-height: calc(100vh - 140px); }
.toolbar { margin-bottom: 20px; }
code { background: #f5f7fa; padding: 2px 6px; border-radius: 4px; font-size: 13px; }
</style>
