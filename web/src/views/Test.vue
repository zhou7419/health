<template>
  <div class="page-container">
    <div class="toolbar">
      <h3>系统诊断</h3>
    </div>

    <el-alert title="此页面仅管理员可见" type="warning" :closable="false" show-icon style="margin-bottom: 16px;" />

    <el-row :gutter="16">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>前端信息</template>
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="构建时间">{{ buildTime }}</el-descriptions-item>
            <el-descriptions-item label="页面加载时间">{{ loadTime }}</el-descriptions-item>
            <el-descriptions-item label="浏览器">{{ browserInfo }}</el-descriptions-item>
            <el-descriptions-item label="前端地址">{{ windowLocation }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <span>后端状态</span>
            <el-tag v-if="backendStatus === 'ok'" type="success" size="small" style="margin-left: 8px;">正常</el-tag>
            <el-tag v-else-if="backendStatus === 'degraded'" type="warning" size="small" style="margin-left: 8px;">降级</el-tag>
            <el-tag v-else type="danger" size="small" style="margin-left: 8px;">异常</el-tag>
          </template>
          <el-descriptions :column="1" border size="small" v-if="backendInfo">
            <el-descriptions-item label="状态">{{ backendInfo.status }}</el-descriptions-item>
            <el-descriptions-item label="数据库">{{ backendInfo.database }}</el-descriptions-item>
            <el-descriptions-item label="运行时长">{{ formatUptime(backendInfo.uptime) }}</el-descriptions-item>
          </el-descriptions>
          <el-empty v-else description="无法连接后端" />
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" style="margin-top: 16px;">
      <template #header>接口连通性测试</template>
      <el-button @click="runTests" :loading="testing" type="primary">运行检测</el-button>
      <el-table v-if="testResults.length > 0" :data="testResults" border style="margin-top: 12px;" size="small">
        <el-table-column prop="name" label="接口" width="200" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === '✅' ? 'success' : 'danger'" size="small">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="detail" label="信息" />
      </el-table>
    </el-card>

    <el-card shadow="hover" style="margin-top: 16px;">
      <template #header>环境变量检查</template>
      <el-descriptions :column="1" border size="small">
        <el-descriptions-item label="后端 API 地址">{{ apiBaseUrl }}</el-descriptions-item>
        <el-descriptions-item label="路由模式">History</el-descriptions-item>
        <el-descriptions-item label="Vue 版本">3</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../utils/api'

const buildTime = ref(document.lastModified ? new Date(document.lastModified).toLocaleString('zh-CN') : new Date().toLocaleString('zh-CN'))
const loadTime = ref('')
const browserInfo = ref('')
const windowLocation = ref('')
const backendInfo = ref(null)
const backendStatus = ref('')
const testing = ref(false)
const testResults = ref([])
const apiBaseUrl = ref('')

// 构建时间 —— Vite 注入
const BUILD_TIME = new Date().toISOString()

onMounted(async () => {
  loadTime.value = new Date().toLocaleString('zh-CN')
  browserInfo.value = navigator.userAgent.substring(0, 80) + '...'
  windowLocation.value = window.location.href
  apiBaseUrl.value = api.defaults?.baseURL || '/api/v1'

  try {
    const healthRes = await api.get('/stats/health')
    backendInfo.value = healthRes.data
    backendStatus.value = healthRes.data.status
  } catch (e) {
    backendStatus.value = 'error'
  }
})

const formatUptime = (seconds) => {
  if (!seconds && seconds !== 0) return '-'
  const d = Math.floor(seconds / 86400)
  const h = Math.floor((seconds % 86400) / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  return `${d}天 ${h}时 ${m}分 ${s}秒`
}

const runTests = async () => {
  testing.value = true
  testResults.value = []

  const endpoints = [
    { name: 'Auth - GET /auth/me', url: '/auth/me' },
    { name: 'Stats - GET /stats/stats', url: '/stats/stats' },
    { name: 'Health - GET /stats/health', url: '/stats/health' },
    { name: 'Persons - GET /persons/', url: '/persons/?page_size=1' },
    { name: 'Definitions - GET /definitions/', url: '/definitions/?page_size=1' },
    { name: 'Metrics - GET /metrics/', url: '/metrics/?page_size=1' },
  ]

  for (const ep of endpoints) {
    try {
      let res
      if (ep.direct) {
        res = await fetch(ep.url)
        const data = await res.json()
        testResults.value.push({ name: ep.name, status: res.ok ? '✅' : '❌', detail: JSON.stringify(data) })
      } else {
        res = await api.get(ep.url)
        testResults.value.push({ name: ep.name, status: '✅', detail: `${res.status} OK` })
      }
    } catch (e) {
      testResults.value.push({ name: ep.name, status: '❌', detail: e.message || '请求失败' })
    }
  }

  testing.value = false
}
</script>

<style scoped>
.page-container { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05); min-height: calc(100vh - 140px); }
.toolbar { margin-bottom: 20px; }
</style>
