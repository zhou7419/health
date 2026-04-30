<template>
  <div class="page-container">
    <div class="toolbar" style="justify-content: flex-start; gap: 20px; align-items: center;">
      <el-select v-model="advicePersonId" placeholder="选择需要生成报告的人员" style="width: 250px;">
        <el-option v-for="p in persons" :key="p.id" :label="p.name" :value="p.id"></el-option>
      </el-select>
      <el-button type="primary" @click="generateAdvice" :loading="generatingAdvice" :disabled="!advicePersonId">
        <el-icon style="margin-right: 5px;"><MagicStick /></el-icon> 生成专属健康建议
      </el-button>
    </div>

    <el-card v-if="adviceHtml || generatingAdvice" shadow="never" style="margin-top: 20px;">
      <el-skeleton :rows="10" animated :loading="generatingAdvice">
        <template #default>
          <div class="advice-content" v-html="adviceHtml"></div>
        </template>
      </el-skeleton>
    </el-card>

    <div v-else style="text-align: center; color: #909399; margin-top: 100px;">
      <el-icon style="font-size: 48px; margin-bottom: 10px;"><FirstAidKit /></el-icon>
      <p>选择人员并点击“生成”，AI 将分析其所有历史体检指标并给出改善建议。</p>
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

const fetchPersons = async () => {
  try {
    const res = await api.get('/persons/?limit=100')
    persons.value = res.data
  } catch (error) {}
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
    adviceHtml.value = marked.parse(res.data.advice)
    ElMessage.success('健康报告生成完毕！')
  } catch (error) {
    const errorMsg = error.response?.data?.detail || '生成建议失败'
    ElMessage.error(errorMsg)
  } finally {
    loadingMsg.close()
    generatingAdvice.value = false
  }
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
</style>