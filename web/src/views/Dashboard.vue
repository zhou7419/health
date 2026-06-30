<template>
  <div class="page-container">
    <div class="toolbar">
      <h3>数据概览</h3>
    </div>

    <div class="stat-cards">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-value">{{ stats.total_persons }}</div>
        <div class="stat-label">人员总数</div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-value">{{ stats.total_definitions }}</div>
        <div class="stat-label">指标类型</div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-value">{{ stats.total_records }}</div>
        <div class="stat-label">体检记录</div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-value">{{ stats.recent_7d_records }}</div>
        <div class="stat-label">最近7天新增</div>
      </el-card>
    </div>

    <div class="chart-section">
      <el-card shadow="hover">
        <template #header>各人员记录数 TOP5</template>
        <div v-if="stats.person_rank && stats.person_rank.length > 0">
          <div v-for="(item, i) in stats.person_rank" :key="i" class="rank-row">
            <span class="rank-label">{{ item.name }}</span>
            <span class="rank-bar-bg">
              <span class="rank-bar" :style="{ width: (item.count / maxCount * 100) + '%' }"></span>
            </span>
            <span class="rank-count">{{ item.count }} 条</span>
          </div>
        </div>
        <el-empty v-else description="暂无数据" />
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../utils/api'

const stats = ref({})

const maxCount = computed(() => {
  const ranks = stats.value.person_rank || []
  return ranks.length > 0 ? Math.max(...ranks.map(r => r.count)) : 1
})

onMounted(async () => {
  try {
    const res = await api.get('/stats/stats')
    stats.value = res.data
  } catch (e) {
    ElMessage.error('获取统计数据失败')
  }
})
</script>

<style scoped>
.page-container { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05); min-height: calc(100vh - 140px); }
.toolbar { margin-bottom: 20px; }
.stat-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
.stat-card { text-align: center; }
.stat-value { font-size: 36px; font-weight: 700; color: #409EFF; }
.stat-label { font-size: 14px; color: #909399; margin-top: 8px; }
.chart-section { max-width: 500px; }
.rank-row { display: flex; align-items: center; margin-bottom: 12px; gap: 12px; }
.rank-label { width: 80px; font-size: 14px; color: #303133; }
.rank-bar-bg { flex: 1; height: 20px; background: #f0f2f5; border-radius: 4px; overflow: hidden; }
.rank-bar { display: block; height: 100%; background: linear-gradient(90deg, #409EFF, #79bbff); border-radius: 4px; transition: width 0.6s; }
.rank-count { width: 60px; text-align: right; font-size: 13px; color: #606266; }
</style>
