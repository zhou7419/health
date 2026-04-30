<template>
  <div class="page-container">
    <div class="toolbar" style="justify-content: flex-start; gap: 20px;">
      <el-select v-model="analysisPersonId" placeholder="选择人员" @change="loadAnalysisChart" style="width: 200px;">
        <el-option v-for="p in persons" :key="p.id" :label="p.name" :value="p.id"></el-option>
      </el-select>
      <el-select v-model="analysisMetricId" placeholder="选择指标" @change="loadAnalysisChart" style="width: 250px;">
        <el-option v-for="def in definitions" :key="def.id" :label="def.name" :value="def.id"></el-option>
      </el-select>
    </div>

    <div v-show="!analysisMetricId || !analysisPersonId" style="text-align: center; color: #909399; margin-top: 100px;">
      请先选择人员和指标以查看趋势分析图表
    </div>
    
    <div v-show="analysisMetricId && analysisPersonId" id="analysis-chart" class="chart-container" style="width: 100%; height: 500px; margin-top: 20px;"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import api from '../utils/api'

const persons = ref([])
const definitions = ref([])
const analysisPersonId = ref('')
const analysisMetricId = ref('')
let chartInstance = null

const fetchPersons = async () => {
  try {
    const res = await api.get('/persons/?limit=100')
    persons.value = res.data
  } catch (error) {}
}

const fetchDefinitions = async () => {
  try {
    const res = await api.get('/definitions/?limit=1000')
    definitions.value = res.data
  } catch (error) {}
}

const loadAnalysisChart = async () => {
  if (!analysisPersonId.value || !analysisMetricId.value) return

  const chartDom = document.getElementById('analysis-chart')
  if (!chartInstance) {
    chartInstance = echarts.init(chartDom)
  }
  chartInstance.showLoading()

  try {
    const res = await api.get(`/metrics/${analysisMetricId.value}/history?person_id=${analysisPersonId.value}`)
    const data = res.data
    
    if (data.length === 0) {
      chartInstance.hideLoading()
      chartInstance.clear()
      ElMessage.warning('该人员此指标暂无历史数据')
      return
    }

    const def = data[0].metric
    const person = data[0].person
    const dates = data.map(item => item.record_date)
    const values = data.map(item => item.value)

    const option = {
      title: {
        text: `${person.name} - ${def.name} 趋势分析`,
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        formatter: function(params) {
          const item = params[0]
          return `${item.axisValue}<br/>${item.marker} ${item.seriesName}: <b>${item.value}</b> ${def.unit || ''}`
        }
      },
      xAxis: {
        type: 'category',
        data: dates,
        name: '日期'
      },
      yAxis: {
        type: 'value',
        name: `数值 (${def.unit || ''})`,
        scale: true
      },
      series: [
        {
          name: def.name,
          type: 'line',
          data: values,
          smooth: true,
          markPoint: {
            data: [
              { type: 'max', name: '最大值' },
              { type: 'min', name: '最小值' }
            ]
          },
          markLine: {
            data: []
          },
          markArea: {
            itemStyle: {
              color: 'rgba(103, 194, 58, 0.1)'
            },
            data: []
          }
        }
      ]
    }

    if (def.expected_min != null || def.expected_max != null) {
      const markLineData = []
      const yAxisArea = []

      if (def.expected_min != null) {
        markLineData.push({ yAxis: def.expected_min, name: '下限', lineStyle: { color: '#E6A23C' } })
        yAxisArea.push({ yAxis: def.expected_min })
      } else {
        yAxisArea.push({ yAxis: 'min' })
      }

      if (def.expected_max != null) {
        markLineData.push({ yAxis: def.expected_max, name: '上限', lineStyle: { color: '#F56C6C' } })
        yAxisArea.push({ yAxis: def.expected_max })
      } else {
        yAxisArea.push({ yAxis: 'max' })
      }

      option.series[0].markLine.data = markLineData
      option.series[0].markArea.data = [ yAxisArea ]
    }

    chartInstance.setOption(option)
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
.toolbar { margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
</style>