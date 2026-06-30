<template>
  <div class="page-container">
    <div class="toolbar" style="justify-content: flex-start; gap: 12px; align-items: center;">
      <el-select v-model="advicePersonId" placeholder="选择需要生成报告的人员" style="width: 220px;">
        <el-option v-for="p in persons" :key="p.id" :label="p.name" :value="p.id"></el-option>
      </el-select>
      <el-button type="primary" @click="generateAdvice" :loading="generatingAdvice" :disabled="!advicePersonId">
        <el-icon style="margin-right: 5px;"><MagicStick /></el-icon> 生成健康建议
      </el-button>
      <el-button @click="showHistory = !showHistory">
        {{ showHistory ? '关闭历史' : '查看历史' }}
      </el-button>
    </div>

    <!-- 历史记录列表 -->
    <el-collapse-transition>
      <el-card v-if="showHistory" shadow="hover" style="margin-top: 16px;">
        <template #header>历史建议记录</template>
        <div v-if="historyList.length === 0" style="text-align: center; color: #909399; padding: 20px;">
          暂无历史建议
        </div>
        <div v-for="item in historyList" :key="item.id" class="history-item">
          <div class="history-meta">
            <span class="history-date">{{ formatDate(item.created_at) }}</span>
            <span class="history-summary">{{ item.summary || '健康建议报告' }}</span>
          </div>
          <div class="history-actions">
            <el-button size="small" type="primary" link @click="viewHistory(item)">查看</el-button>
            <el-popconfirm title="确定删除？" @confirm="deleteHistory(item.id)">
              <template #reference>
                <el-button size="small" type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </div>
        </div>
        <div v-if="historyList.length > 0" style="margin-top: 12px;">
          <el-pagination
            v-model:current-page="historyPage"
            :page-size="10"
            :total="historyTotal"
            small
            layout="prev, pager, next"
            @current-change="fetchHistory"
          />
        </div>
      </el-card>
    </el-collapse-transition>

    <!-- 建议内容 -->
    <el-card v-if="adviceHtml || generatingAdvice" shadow="never" style="margin-top: 16px;">
      <el-skeleton :rows="10" animated :loading="generatingAdvice">
        <template #default>
          <div class="advice-content" v-html="adviceHtml"></div>
        </template>
      </el-skeleton>
    </el-card>

    <div v-else-if="!showHistory" style="text-align: center; color: #909399; margin-top: 100px;">
      <el-icon style="font-size: 48px; margin-bottom: 10px;"><FirstAidKit /></el-icon>
      <p>选择人员并点击"生成"，AI 将分析其所有历史体检指标并给出改善建议。</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { MagicStick, FirstAidKit } from '@element-plus/icons-vue'
import { marked } from 'marked'
import api from '../utils/api'

const persons = ref([])
const advicePersonId = ref('')
const adviceHtml = ref('')
const generatingAdvice = ref(false)
const showHistory = ref(false)
const historyList = ref([])
const historyPage = ref(1)
const historyTotal = ref(0)

const fetchPersons = async () => {
  try {
    const res = await api.get('/persons/', { params: { page: 1, page_size: 100 } })
    persons.value = res.data.items
  } catch (error) {}
}

const fetchHistory = async () => {
  try {
    const params = { page: historyPage.value, page_size: 10 }
    if (advicePersonId.value) params.person_id = advicePersonId.value
    const res = await api.get('/advices/', { params })
    historyList.value = res.data.items
    historyTotal.value = res.data.total
  } catch (e) {
    historyList.value = []
  }
}

const generateAdvice = async () => {
  if (!advicePersonId.value) return
  generatingAdvice.value = true
  adviceHtml.value = ''

  const loadingMsg = ElMessage({
    message: 'AI 医生正在分析您的所有体检指标历史，撰写专属健康报告，请稍候...',
    type: 'info',
    duration: 0,
    icon: 'Loading'
  })

  try {
    const res = await api.post('/smart/advice', { person_id: advicePersonId.value })
    const html = marked.parse(res.data.advice)
    adviceHtml.value = html
    ElMessage.success('健康报告生成完毕！')

    // 自动保存到历史
    const person = persons.value.find(p => p.id === advicePersonId.value)
    await api.post('/advices/', {
      person_id: advicePersonId.value,
      content: res.data.advice,
      summary: `${person?.name || ''} 健康建议 ${new Date().toLocaleDateString()}`
    })
    fetchHistory()
  } catch (error) {
    const errorMsg = error.response?.data?.detail || '生成建议失败'
    ElMessage.error(errorMsg)
  } finally {
    loadingMsg.close()
    generatingAdvice.value = false
  }
}

const viewHistory = (item) => {
  adviceHtml.value = marked.parse(item.content)
  showHistory.value = false
}

const deleteHistory = async (id) => {
  try {
    await api.delete(`/advices/${id}`)
    ElMessage.success('已删除')
    fetchHistory()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

const formatDate = (d) => {
  if (!d) return ''
  return new Date(d).toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}

onMounted(() => {
  fetchPersons()
})
</script>

<style scoped>
.page-container { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05); min-height: calc(100vh - 140px); }
.toolbar { margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
.advice-content :deep(h1), .advice-content :deep(h2), .advice-content :deep(h3) { color: #2c3e50; }
.advice-content :deep(ul) { padding-left: 20px; }
.advice-content :deep(li) { margin-bottom: 8px; }
.history-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #f0f2f5; }
.history-item:last-child { border-bottom: none; }
.history-meta { flex: 1; }
.history-date { font-size: 12px; color: #909399; margin-right: 12px; }
.history-summary { font-size: 14px; color: #303133; }
.history-actions { display: flex; gap: 8px; }
</style>
