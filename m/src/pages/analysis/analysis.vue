<template>
  <view class="page-wrap">
    <!-- 选择器 -->
    <view class="card">
      <view class="form-row">
        <text class="form-label">人员</text>
        <picker mode="selector" :range="persons" range-key="name" @change="onPersonChange">
          <view class="picker-val" :class="{ placeholder: !selectedPerson }">
            {{ selectedPerson || '请选择' }}
          </view>
        </picker>
      </view>

      <view class="form-row">
        <text class="form-label">指标</text>
        <picker mode="selector" :range="definitions" range-key="name" @change="onMetricChange">
          <view class="picker-val" :class="{ placeholder: !selectedMetric }">
            {{ selectedMetric || '请选择' }}
          </view>
        </picker>
      </view>
    </view>

    <!-- 提示 -->
    <view v-if="!personId || !metricId" class="empty-state">
      <text class="empty-icon">📈</text>
      <text class="empty-text">请选择人员和指标以查看趋势分析</text>
    </view>

    <!-- 图表 + 数据 -->
    <view v-if="personId && metricId && historyData.length" class="card">
      <view class="chart-header">
        <text class="chart-title">{{ selectedPerson }} - {{ selectedMetric }}</text>
        <text class="chart-sub">共 {{ historyData.length }} 次记录</text>
      </view>

      <!-- Canvas 简易折线图 -->
      <view class="chart-container">
        <canvas
          type="2d"
          id="lineChart"
          class="line-canvas"
          @touchstart="onChartTouch"
        ></canvas>
      </view>

      <!-- 统计 -->
      <view class="stats-row">
        <view class="stat-item">
          <text class="stat-value" :class="stats.isNormal === true ? 'val-normal' : stats.isNormal === false ? 'val-abnormal' : ''">
            {{ stats.latest }}
          </text>
          <text class="stat-label">最新值</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ stats.max }}</text>
          <text class="stat-label">最高</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ stats.min }}</text>
          <text class="stat-label">最低</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ stats.avg }}</text>
          <text class="stat-label">平均</text>
        </view>
      </view>

      <view v-if="rangeText" class="range-bar">
        <text class="range-label">参考范围：{{ rangeText }}</text>
      </view>

      <!-- 历史数据列表 -->
      <view class="history-title">历史记录</view>
      <view v-for="(h, i) in historyData" :key="i" class="history-item flex-between">
        <text class="h-date">{{ h.record_date }}</text>
        <view class="flex-row">
          <text :class="['h-value', getValueClass(h.value)]">{{ h.value }}</text>
          <text class="h-trend">{{ getTrendIcon(i) }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import api from '@/api/index.js'
import { checkAuth } from '@/router.js'

const persons = ref([])
const definitions = ref([])
const personId = ref('')
const metricId = ref('')
const selectedPerson = ref('')
const selectedMetric = ref('')
const historyData = ref([])
const rangeText = ref('')
let canvasCtx = null

// 图表配置
const chartConfig = computed(() => {
  const data = historyData.value
  if (!data.length) return null
  const values = data.map(h => h.value)
  const meta = data[0]?.metric
  return {
    values,
    dates: data.map(h => h.record_date),
    expectedMin: meta?.expected_min,
    expectedMax: meta?.expected_max,
    unit: meta?.unit || ''
  }
})

// 统计数据
const stats = computed(() => {
  if (!historyData.value.length) return null
  const values = historyData.value.map(h => h.value)
  const latest = values[values.length - 1]
  const max = Math.max(...values)
  const min = Math.min(...values)
  const avg = (values.reduce((a, b) => a + b, 0) / values.length).toFixed(1)

  const meta = historyData.value[0]?.metric
  let isNormal = null
  if (meta) {
    if (meta.expected_min != null && latest < meta.expected_min) isNormal = false
    else if (meta.expected_max != null && latest > meta.expected_max) isNormal = false
    else if (meta.expected_min != null || meta.expected_max != null) isNormal = true
  }

  return { latest, max, min, avg, isNormal }
})

// 趋势箭头
const getTrendIcon = (i) => {
  if (i === 0) return ''
  const prev = historyData.value[i - 1].value
  const curr = historyData.value[i].value
  if (curr > prev) return '↑'
  if (curr < prev) return '↓'
  return '→'
}

const getValueClass = (val) => {
  const meta = historyData.value[0]?.metric
  if (!meta) return ''
  if (meta.expected_min != null && val < meta.expected_min) return 'val-abnormal'
  if (meta.expected_max != null && val > meta.expected_max) return 'val-abnormal'
  if (meta.expected_min != null || meta.expected_max != null) return 'val-normal'
  return ''
}

// 绘制 Canvas 折线图
const drawChart = () => {
  const config = chartConfig.value
  if (!config || !config.values.length) return

  nextTick(() => {
    const query = uni.createSelectorQuery()
    query.select('#lineChart')
      .fields({ node: true, size: true })
      .exec((res) => {
        if (!res[0] || !res[0].node) return

        const canvas = res[0].node
        const ctx = canvas.getContext('2d')
        const dpr = uni.getSystemInfoSync().pixelRatio

        const width = res[0].width
        const height = res[0].height
        canvas.width = width * dpr
        canvas.height = height * dpr
        ctx.scale(dpr, dpr)

        canvasCtx = ctx

        const padding = { top: 20, right: 20, bottom: 40, left: 50 }
        const chartW = width - padding.left - padding.right
        const chartH = height - padding.top - padding.bottom

        const values = config.values
        const minVal = Math.min(...values)
        const maxVal = Math.max(...values)
        const range = maxVal - minVal || 1

        // 扩展 Y 轴范围
        const yMin = Math.min(minVal, config.expectedMin ?? minVal) - range * 0.1
        const yMax = Math.max(maxVal, config.expectedMax ?? maxVal) + range * 0.1
        const yRange = yMax - yMin || 1

        // 清空
        ctx.clearRect(0, 0, width, height)

        // 背景网格
        ctx.strokeStyle = '#f0f0f0'
        ctx.lineWidth = 1
        for (let i = 0; i <= 4; i++) {
          const y = padding.top + (chartH / 4) * i
          ctx.beginPath()
          ctx.moveTo(padding.left, y)
          ctx.lineTo(width - padding.right, y)
          ctx.stroke()

          // Y 轴标签
          const label = (yMax - (yRange / 4) * i).toFixed(1)
          ctx.fillStyle = '#909399'
          ctx.font = '10px sans-serif'
          ctx.textAlign = 'right'
          ctx.fillText(label, padding.left - 5, y + 4)
        }

        // 参考范围线
        if (config.expectedMin != null) {
          const y = padding.top + chartH - ((config.expectedMin - yMin) / yRange) * chartH
          ctx.strokeStyle = '#E6A23C'
          ctx.lineWidth = 1
          ctx.setLineDash([5, 3])
          ctx.beginPath()
          ctx.moveTo(padding.left, y)
          ctx.lineTo(width - padding.right, y)
          ctx.stroke()
          ctx.setLineDash([])
          ctx.fillStyle = '#E6A23C'
          ctx.fillText(`下限 ${config.expectedMin}`, width - padding.right - 60, y - 4)
        }

        if (config.expectedMax != null) {
          const y = padding.top + chartH - ((config.expectedMax - yMin) / yRange) * chartH
          ctx.strokeStyle = '#F56C6C'
          ctx.lineWidth = 1
          ctx.setLineDash([5, 3])
          ctx.beginPath()
          ctx.moveTo(padding.left, y)
          ctx.lineTo(width - padding.right, y)
          ctx.stroke()
          ctx.setLineDash([])
          ctx.fillStyle = '#F56C6C'
          ctx.fillText(`上限 ${config.expectedMax}`, width - padding.right - 60, y - 4)
        }

        // 折线
        if (values.length > 1) {
          ctx.strokeStyle = '#409EFF'
          ctx.lineWidth = 2.5
          ctx.lineJoin = 'round'
          ctx.beginPath()
          values.forEach((v, i) => {
            const x = padding.left + (chartW / (values.length - 1)) * i
            const y = padding.top + chartH - ((v - yMin) / yRange) * chartH
            if (i === 0) ctx.moveTo(x, y)
            else ctx.lineTo(x, y)
          })
          ctx.stroke()

          // 数据点
          values.forEach((v, i) => {
            const x = padding.left + (chartW / (values.length - 1)) * i
            const y = padding.top + chartH - ((v - yMin) / yRange) * chartH

            ctx.fillStyle = '#fff'
            ctx.strokeStyle = '#409EFF'
            ctx.lineWidth = 2
            ctx.beginPath()
            ctx.arc(x, y, 5, 0, Math.PI * 2)
            ctx.fill()
            ctx.stroke()

            // X 轴标签
            const dateStr = config.dates[i] || ''
            const shortDate = dateStr.length > 7 ? dateStr.slice(5) : dateStr
            ctx.fillStyle = '#909399'
            ctx.font = '9px sans-serif'
            ctx.textAlign = 'center'
            ctx.fillText(shortDate, x, height - padding.bottom + 20)
          })
        }
      })
  })
}

const onChartTouch = (e) => {
  // 预留交互
}

// 数据加载
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

const onPersonChange = (e) => {
  const p = persons.value[e.detail.value]
  personId.value = p.id
  selectedPerson.value = p.name
  loadHistory()
}

const onMetricChange = (e) => {
  const d = definitions.value[e.detail.value]
  metricId.value = d.id
  selectedMetric.value = d.name
  rangeText.value = ''
  if (d.expected_min != null && d.expected_max != null) {
    rangeText.value = `${d.expected_min} - ${d.expected_max} ${d.unit || ''}`
  } else if (d.expected_min != null) {
    rangeText.value = `≥ ${d.expected_min} ${d.unit || ''}`
  } else if (d.expected_max != null) {
    rangeText.value = `≤ ${d.expected_max} ${d.unit || ''}`
  }
  loadHistory()
}

const loadHistory = async () => {
  if (!personId.value || !metricId.value) return
  try {
    const res = await api.get(`/metrics/${metricId.value}/history`, {
      person_id: personId.value
    })
    historyData.value = Array.isArray(res) ? res : []
    // 数据加载后绘制图表
    setTimeout(() => drawChart(), 300)
  } catch (e) {
    historyData.value = []
  }
}

onMounted(() => {
  checkAuth()
  fetchPersons()
  fetchDefinitions()
})

// 监听数据变化重绘
watch(historyData, () => {
  setTimeout(() => drawChart(), 300)
})
</script>

<style lang="scss" scoped>
.form-row {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;

  .form-label {
    width: 120rpx;
    font-size: 28rpx;
    color: #606266;
  }

  .picker-val {
    flex: 1;
    font-size: 28rpx;
    padding: 12rpx 16rpx;
    background: #f5f7fa;
    border-radius: 8rpx;
    color: #303133;

    &.placeholder { color: #c0c4cc; }
  }
}

.chart-header {
  text-align: center;
  margin-bottom: 20rpx;

  .chart-title {
    font-size: 32rpx;
    font-weight: bold;
    color: #303133;
    display: block;
  }

  .chart-sub {
    font-size: 24rpx;
    color: #c0c4cc;
    margin-top: 4rpx;
  }
}

.chart-container {
  width: 100%;
  height: 400rpx;
  margin-bottom: 20rpx;

  .line-canvas {
    width: 100%;
    height: 100%;
  }
}

.stats-row {
  display: flex;
  justify-content: space-around;
  margin-bottom: 16rpx;
  padding-bottom: 20rpx;
  border-bottom: 1rpx solid #f0f0f0;

  .stat-item {
    text-align: center;

    .stat-value {
      font-size: 34rpx;
      font-weight: bold;
      color: #303133;
      display: block;
    }

    .stat-label {
      font-size: 22rpx;
      color: #c0c4cc;
      margin-top: 4rpx;
    }
  }
}

.range-bar {
  margin-bottom: 24rpx;
  padding: 16rpx;
  background: #f5f7fa;
  border-radius: 8rpx;
  text-align: center;

  .range-label {
    font-size: 24rpx;
    color: #606266;
  }
}

.history-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #303133;
  margin-bottom: 16rpx;
  padding-top: 16rpx;
  border-top: 1rpx solid #f0f0f0;
}

.history-item {
  padding: 14rpx 0;
  border-bottom: 1rpx solid #f5f7fa;

  .h-date {
    font-size: 26rpx;
    color: #606266;
  }

  .h-value {
    font-size: 30rpx;
    font-weight: bold;
    margin-right: 12rpx;
  }

  .h-trend {
    font-size: 28rpx;
    color: #909399;
    width: 40rpx;
    text-align: center;
  }
}
</style>
