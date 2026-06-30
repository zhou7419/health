<template>
  <div class="page-container">
    <div class="toolbar" style="flex-wrap: wrap; gap: 12px;">
      <el-select v-model="selectedPersons" placeholder="选择人员（可多选）" multiple collapse-tags style="width: 220px;">
        <el-option v-for="p in persons" :key="p.id" :label="p.name" :value="p.id"></el-option>
      </el-select>
      <el-select v-model="selectedMetrics" placeholder="选择指标（可多选）" multiple collapse-tags style="width: 280px;">
        <el-option v-for="def in definitions" :key="def.id" :label="def.name" :value="def.id"></el-option>
      </el-select>
      <el-button type="primary" @click="loadAnalysisChart" :disabled="selectedPersons.length === 0 || selectedMetrics.length === 0">查询对比</el-button>
      <el-button @click="clearAll">清空</el-button>
    </div>

    <div v-if="noData" style="text-align: center; color: #909399; margin-top: 100px;">
      请选择人员和指标，点击"查询对比"查看趋势图表
    </div>

    <div v-show="!noData" id="analysis-chart" class="chart-container" style="width: 100%; height: 500px; margin-top: 20px;"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import api from '../utils/api'

const persons = ref([])
const definitions = ref([])
const selectedPersons = ref([])
const selectedMetrics = ref([])
const noData = ref(true)
let chartInstance = null

const COLORS = ['#409EFF', '#F56C6C', '#67C23A', '#E6A23C', '#9B59B6', '#1ABC9C', '#E74C3C', '#3498DB']

const fetchPersons = async () => {
  try {
    const res = await api.get('/persons/', { params: { page: 1, page_size: 100 } })
    persons.value = res.data.items
  } catch (error) {}
}

const fetchDefinitions = async () => {
  try {
    const res = await api.get('/definitions/', { params: { page: 1, page_size: 1000 } })
    definitions.value = res.data.items
  } catch (error) {}
}

const clearAll = () => {
  selectedPersons.value = []
  selectedMetrics.value = []
  noData.value = true
  if (chartInstance) {
    chartInstance.clear()
  }
}

const loadAnalysisChart = async () => {
  if (selectedPersons.value.length === 0 || selectedMetrics.value.length === 0) return

  const chartDom = document.getElementById('analysis-chart')
  if (!chartInstance) {
    chartInstance = echarts.init(chartDom)
  }
  chartInstance.showLoading()
  noData.value = false

  try {
    // 并发请求所有选中组合的历史数据
    const queries = []
    for (const pid of selectedPersons.value) {
      for (const mid of selectedMetrics.value) {
        queries.push(
          api.get(`/metrics/${mid}/history?person_id=${pid}`)
            .then(res => ({ personId: pid, metricId: mid, data: res.data }))
            .catch(() => ({ personId: pid, metricId: mid, data: [] }))
        )
      }
    }

    const results = await Promise.all(queries)
    const validResults = results.filter(r => r.data.length > 0)

    if (validResults.length === 0) {
      chartInstance.hideLoading()
      chartInstance.clear()
      ElMessage.warning('所选组合均无历史数据')
      return
    }

    // 收集所有日期（去重排序）
    const allDates = [...new Set(validResults.flatMap(r => r.data.map(d => d.record_date)))].sort()

    // 构建 series
    const series = []
    const legendData = []
    let colorIdx = 0

    for (const r of validResults) {
      const person = persons.value.find(p => p.id === r.personId)
      const metric = definitions.value.find(d => d.id === r.metricId)
      const label = `${person?.name || '?'} - ${metric?.name || '?'}`
      legendData.push(label)

      // 按日期对齐数据
      const dateMap = {}
      for (const d of r.data) {
        dateMap[d.record_date] = d.value
      }
      const values = allDates.map(date => dateMap[date] ?? null)

      const color = COLORS[colorIdx % COLORS.length]
      colorIdx++

      const lineSeries = {
        name: label,
        type: 'line',
        data: values,
        smooth: true,
        lineStyle: { color },
        itemStyle: { color },
        symbol: 'circle'
      }

      // 添加参考区间（取第一个 metric 定义的期望范围）
      if (r.data[0]?.metric) {
        const def = r.data[0].metric
        if (def.expected_min != null || def.expected_max != null) {
          lineSeries.markLine = { data: [] }
          if (def.expected_min != null) {
            lineSeries.markLine.data.push({ yAxis: def.expected_min, name: `${label} 下限`, lineStyle: { color: '#E6A23C', type: 'dashed' } })
          }
          if (def.expected_max != null) {
            lineSeries.markLine.data.push({ yAxis: def.expected_max, name: `${label} 上限`, lineStyle: { color: '#F56C6C', type: 'dashed' } })
          }
        }
      }

      series.push(lineSeries)
    }

    const option = {
      title: {
        text: '指标趋势对比',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        formatter: function(params) {
          let html = `<b>${params[0].axisValue}</b><br/>`
          for (const p of params) {
            if (p.value != null) {
              html += `${p.marker} ${p.seriesName}: <b>${p.value}</b><br/>`
            }
          }
          return html
        }
      },
      legend: { data: legendData, top: 40, type: 'scroll' },
      grid: { top: 90, bottom: 30 },
      xAxis: {
        type: 'category',
        data: allDates,
        name: '日期',
        axisLabel: { rotate: 45 }
      },
      yAxis: {
        type: 'value',
        name: '数值',
        scale: true
      },
      dataZoom: [
        { type: 'inside', start: 0, end: 100 },
        { type: 'slider', start: 0, end: 100 }
      ],
      series
    }

    chartInstance.setOption(option, true)
    chartInstance.hideLoading()
  } catch (error) {
    chartInstance.hideLoading()
    ElMessage.error('获取趋势数据失败')
  }
}

const handleResize = () => {
  if (chartInstance) chartInstance.resize()
}

onMounted(() => {
  fetchPersons()
  fetchDefinitions()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (chartInstance) chartInstance.dispose()
})
</script>

<style scoped>
.page-container { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05); min-height: calc(100vh - 140px); }
.toolbar { margin-bottom: 20px; display: flex; align-items: center; }
</style>
