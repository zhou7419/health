<template>
  <view class="page-wrap">
    <view class="card">
      <view class="section-title">基本信息</view>

      <!-- 人员选择 -->
      <view class="form-row">
        <text class="form-label required">人员</text>
        <picker mode="selector" :range="persons" range-key="name" @change="onPersonChange">
          <view class="picker-val" :class="{ placeholder: !form.personName }">
            {{ form.personName || '请选择人员' }}
          </view>
        </picker>
      </view>

      <!-- 日期选择 -->
      <view class="form-row">
        <text class="form-label required">体检日期</text>
        <picker mode="date" :value="form.recordDate" @change="onDateChange">
          <view class="picker-val">{{ form.recordDate }}</view>
        </picker>
      </view>
    </view>

    <!-- 录入方式 -->
    <view class="card">
      <view class="section-title">录入方式</view>
      <view class="segmented">
        <view
          v-for="tab in tabs"
          :key="tab.key"
          :class="['seg-item', { active: activeTab === tab.key }]"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </view>
      </view>

      <!-- 文本/JSON 输入 -->
      <view v-if="activeTab === 'text'" class="tab-content">
        <textarea
          class="text-area"
          v-model="textInput"
          placeholder='粘贴 JSON 或自然语言描述，例如：
{"体重": "70.8", "收缩压": 120}
或
"今天体重 75.2kg，血压 125/80"'
          :maxlength="-1"
        />
        <view class="btn-row">
          <button class="btn-secondary" @click="parseJson">JSON 解析</button>
          <button class="btn-primary" :loading="parsingText" @click="smartParse">
            🤖 AI 智能解析
          </button>
        </view>
      </view>

      <!-- 文件上传 -->
      <view v-if="activeTab === 'file'" class="tab-content">
        <view class="upload-area" @click="chooseFile">
          <text class="upload-icon">📁</text>
          <text class="upload-text">点击选择文件</text>
          <text class="upload-hint">支持图片、PDF、文本文件</text>
        </view>
        <view v-if="uploadedFiles.length" class="file-list">
          <view v-for="(f, i) in uploadedFiles" :key="i" class="file-item">
            <text class="file-name">{{ f.name || '文件 ' + (i + 1) }}</text>
            <text class="file-remove" @click="removeFile(i)">✕</text>
          </view>
        </view>
        <button
          v-if="uploadedFiles.length"
          class="btn-primary"
          :loading="parsingFile"
          @click="smartParseFile"
        >
          🤖 AI 智能解析文件
        </button>
      </view>

      <!-- CSV 导入 -->
      <view v-if="activeTab === 'csv'" class="tab-content">
        <view class="upload-area" @click="chooseCsv">
          <text class="upload-icon">📊</text>
          <text class="upload-text">选择 CSV 文件导入</text>
          <text class="upload-hint">
            表头：指标名称,数值,单位,参考下限,参考上限,备注
          </text>
        </view>
        <view v-if="csvFile" class="file-list">
          <view class="file-item">
            <text class="file-name">{{ csvFile.name || 'CSV文件' }}</text>
            <text class="file-remove" @click="csvFile = null">✕</text>
          </view>
        </view>
        <button
          v-if="csvFile"
          class="btn-primary"
          :loading="uploadingCsv"
          @click="uploadCsv"
        >
          确认导入
        </button>
      </view>
    </view>

    <!-- 指标列表 -->
    <view class="card" v-if="form.metrics.length">
      <view class="section-title flex-between">
        <text>指标列表</text>
        <text class="count-tag">共 {{ validCount }} 项待保存</text>
      </view>

      <view v-for="(m, i) in form.metrics" :key="i" class="metric-row">
        <!-- 指标选择 -->
        <picker
          mode="selector"
          :range="metricPickerOptions"
          range-key="name"
          @change="(e) => onMetricSelect(i, e)"
        >
          <view class="metric-picker">
            {{ getMetricLabel(m) }}
          </view>
        </picker>

        <!-- 自定义名称 -->
        <input
          v-if="m.metric_id === 'custom'"
          class="metric-input"
          v-model="m.customName"
          placeholder="自定义名称"
        />

        <!-- 数值 -->
        <view class="metric-value-row flex-row">
          <input
            class="metric-input number"
            v-model.number="m.value"
            type="digit"
            placeholder="数值"
          />
          <text class="metric-unit-text" v-if="m.metric_id && m.metric_id !== 'custom'">
            {{ getMetricUnit(m.metric_id) }}
          </text>
          <input
            v-else
            class="metric-input unit"
            v-model="m.customUnit"
            placeholder="单位"
          />
        </view>

        <!-- 参考范围（自定义时显示） -->
        <view v-if="!m.metric_id || m.metric_id === 'custom'" class="range-row">
          <input class="metric-input half" v-model.number="m.expected_min" type="digit" placeholder="下限" />
          <text class="range-sep">-</text>
          <input class="metric-input half" v-model.number="m.expected_max" type="digit" placeholder="上限" />
        </view>

        <!-- 备注 -->
        <input class="metric-input" v-model="m.notes" placeholder="备注(可选)" />

        <!-- 删除 -->
        <button class="btn-icon delete" @click="removeMetric(i)">🗑</button>
      </view>

      <button class="btn-add" @click="addMetric">
        <text>＋ 添加一项指标</text>
      </button>
    </view>

    <!-- 保存按钮 -->
    <view class="save-area" v-if="form.metrics.length">
      <button class="btn-save" :loading="submitting" @click="submitBatch">
        保存 {{ validCount }} 条指标记录
      </button>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '@/api/index.js'
import { getToday } from '@/utils/index.js'
import { checkAuth } from '@/router.js'

const persons = ref([])
const definitions = ref([])
const submitting = ref(false)
const activeTab = ref('text')

// 文本输入
const textInput = ref('')
const parsingText = ref(false)
const parsingFile = ref(false)
const uploadingCsv = ref(false)

// 文件上传
const uploadedFiles = ref([])
const csvFile = ref(null)

const tabs = [
  { key: 'text', label: '文本/AI解析' },
  { key: 'file', label: '文件解析' },
  { key: 'csv', label: 'CSV导入' }
]

const form = reactive({
  personId: '',
  personName: '',
  recordDate: getToday(),
  metrics: []
})

const metricPickerOptions = computed(() => [
  ...definitions.value,
  { id: 'custom', name: '+ 自定义指标' }
])

const validCount = computed(() => {
  return form.metrics.filter(m => {
    if (m.value === undefined || m.value === null || m.value === '') return false
    if (m.metric_id === 'custom') return !!m.customName
    return !!m.metric_id
  }).length
})

// 数据获取
const fetchPersons = async () => {
  try {
    persons.value = await api.get('/persons/', { limit: 100 })
    if (persons.value.length && !form.personId) {
      form.personId = persons.value[0].id
      form.personName = persons.value[0].name
    }
  } catch (e) {}
}

const fetchDefinitions = async () => {
  try {
    definitions.value = await api.get('/definitions/', { limit: 1000 })
  } catch (e) {}
}

// 人员/日期选择
const onPersonChange = (e) => {
  const p = persons.value[e.detail.value]
  form.personId = p.id
  form.personName = p.name
}

const onDateChange = (e) => {
  form.recordDate = e.detail.value
}

// 指标管理
const addMetric = () => {
  form.metrics.push({
    metric_id: '',
    customName: '',
    customUnit: '',
    expected_min: undefined,
    expected_max: undefined,
    value: undefined,
    notes: ''
  })
}

const removeMetric = (i) => {
  form.metrics.splice(i, 1)
}

const onMetricSelect = (i, e) => {
  const item = metricPickerOptions.value[e.detail.value]
  form.metrics[i].metric_id = item.id
  if (item.id === 'custom') {
    form.metrics[i].customName = ''
    form.metrics[i].customUnit = ''
    form.metrics[i].expected_min = undefined
    form.metrics[i].expected_max = undefined
  }
}

const getMetricLabel = (m) => {
  if (m.metric_id === 'custom') return '自定义指标 ▼'
  if (!m.metric_id) return '选择指标 ▼'
  const def = definitions.value.find(d => d.id === m.metric_id)
  return def ? `${def.name} ▼` : '选择指标 ▼'
}

const getMetricUnit = (id) => {
  const def = definitions.value.find(d => d.id === id)
  return def?.unit || ''
}

// 解析结果填表
const appendParsedData = (dataObj) => {
  for (const [key, detail] of Object.entries(dataObj)) {
    if (!key) continue
    const existDef = definitions.value.find(d => d.name === key)
    let val = detail
    let unit = ''
    let expected_min = undefined
    let expected_max = undefined

    if (typeof detail === 'object' && detail !== null) {
      val = detail.value
      unit = detail.unit || ''
      expected_min = detail.expected_min
      expected_max = detail.expected_max
    } else {
      val = parseFloat(detail)
    }

    if (isNaN(val)) continue

    const newItem = {
      metric_id: existDef ? existDef.id : 'custom',
      customName: existDef ? '' : key,
      customUnit: unit,
      expected_min,
      expected_max,
      value: val,
      notes: ''
    }

    // 如果第一个是空的，替换掉
    if (form.metrics.length === 1 && !form.metrics[0].metric_id && form.metrics[0].value === undefined) {
      form.metrics = [newItem]
    } else {
      form.metrics.push(newItem)
    }
  }
}

// JSON 解析
const parseJson = () => {
  if (!textInput.value.trim()) return uni.showToast({ title: '请输入数据', icon: 'none' })
  try {
    const data = JSON.parse(textInput.value)
    appendParsedData(data)
    uni.showToast({ title: '解析成功', icon: 'success' })
    textInput.value = ''
  } catch {
    uni.showToast({ title: 'JSON格式错误', icon: 'error' })
  }
}

// AI 智能解析
const smartParse = async () => {
  if (!textInput.value.trim()) return uni.showToast({ title: '请输入文本', icon: 'none' })
  parsingText.value = true
  try {
    const res = await api.post('/smart/', { text: textInput.value })
    appendParsedData(res)
    uni.showToast({ title: 'AI解析成功', icon: 'success' })
    textInput.value = ''
  } catch (e) {}
  parsingText.value = false
}

// 文件选择
const chooseFile = () => {
  uni.chooseFile({
    count: 10,
    type: 'all',
    success: (res) => {
      uploadedFiles.value = res.tempFiles.map(f => ({
        path: f.path,
        name: f.name,
        size: f.size
      }))
    }
  })
}

const chooseCsv = () => {
  uni.chooseFile({
    count: 1,
    type: 'file',
    extension: ['.csv'],
    success: (res) => {
      csvFile.value = {
        path: res.tempFiles[0].path,
        name: res.tempFiles[0].name
      }
    }
  })
}

const removeFile = (i) => {
  uploadedFiles.value.splice(i, 1)
}

const smartParseFile = async () => {
  if (!uploadedFiles.value.length) return
  parsingFile.value = true
  try {
    // 逐个上传文件到 /smart/upload
    const files = uploadedFiles.value.map(f => f.path)
    // 使用 FormData 方式逐个上传
    for (const filePath of files) {
      // 小程序/App 环境用 uni.uploadFile
      const token = uni.getStorageSync('access_token')
      const result = await new Promise((resolve, reject) => {
        uni.uploadFile({
          url: '/api/v1/smart/upload',
          filePath: filePath,
          name: 'files',
          header: {
            'Authorization': token ? `Bearer ${token}` : ''
          },
          success: (res) => {
            try { resolve(JSON.parse(res.data)) }
            catch { resolve(res.data) }
          },
          fail: reject
        })
      })
      appendParsedData(result)
    }
    uni.showToast({ title: '文件解析成功', icon: 'success' })
    uploadedFiles.value = []
  } catch (e) {}
  parsingFile.value = false
}

const uploadCsv = async () => {
  if (!csvFile.value) return
  if (!form.personId) return uni.showToast({ title: '请选择人员', icon: 'none' })

  uploadingCsv.value = true
  try {
    const token = uni.getStorageSync('access_token')
    const result = await new Promise((resolve, reject) => {
      uni.uploadFile({
        url: '/api/v1/metrics/batch/upload',
        filePath: csvFile.value.path,
        name: 'file',
        formData: {
          person_id: String(form.personId),
          record_date: form.recordDate
        },
        header: {
          'Authorization': token ? `Bearer ${token}` : ''
        },
        success: (res) => {
          try { resolve(JSON.parse(res.data)) }
          catch { resolve(res.data) }
        },
        fail: reject
      })
    })
    uni.showToast({ title: `成功导入 ${Array.isArray(result) ? result.length : 0} 条`, icon: 'success' })
    csvFile.value = null
  } catch (e) {}
  uploadingCsv.value = false
}

// 提交保存
const submitBatch = async () => {
  if (!form.personId) return uni.showToast({ title: '请选择人员', icon: 'none' })
  if (!form.recordDate) return uni.showToast({ title: '请选择日期', icon: 'none' })

  const validMetrics = form.metrics.filter(m => {
    if (m.value === undefined || m.value === null || m.value === '') return false
    if (m.metric_id === 'custom') return !!m.customName
    return !!m.metric_id
  })

  if (!validMetrics.length) return uni.showToast({ title: '至少需要一条有效指标', icon: 'none' })

  submitting.value = true
  try {
    await api.post('/metrics/batch', {
      person_id: form.personId,
      record_date: form.recordDate,
      metrics: validMetrics.map(m => ({
        metric_id: m.metric_id === 'custom' ? null : m.metric_id,
        name: m.metric_id === 'custom' ? m.customName : null,
        unit: m.metric_id === 'custom' ? m.customUnit : null,
        expected_min: m.metric_id === 'custom' ? m.expected_min : null,
        expected_max: m.metric_id === 'custom' ? m.expected_max : null,
        value: Number(m.value),
        notes: m.notes || null
      }))
    })
    uni.showToast({ title: `成功保存 ${validMetrics.length} 条记录`, icon: 'success' })
    // 清空表单
    form.metrics = []
    addMetric()
  } catch (e) {}
  submitting.value = false
}

onMounted(() => {
  checkAuth()
  fetchPersons()
  fetchDefinitions()
  addMetric()
})
</script>

<style lang="scss" scoped>
.section-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #303133;
  margin-bottom: 24rpx;
}

.form-row {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;

  .form-label {
    width: 140rpx;
    font-size: 28rpx;
    color: #606266;

    &.required::after {
      content: ' *';
      color: #F56C6C;
    }
  }

  .picker-val {
    flex: 1;
    font-size: 28rpx;
    color: #303133;
    padding: 12rpx 16rpx;
    background: #f5f7fa;
    border-radius: 8rpx;

    &.placeholder { color: #c0c4cc; }
  }
}

// 分段选择器
.segmented {
  display: flex;
  background: #f5f7fa;
  border-radius: 12rpx;
  padding: 6rpx;
  margin-bottom: 24rpx;

  .seg-item {
    flex: 1;
    text-align: center;
    padding: 14rpx 0;
    font-size: 26rpx;
    color: #606266;
    border-radius: 10rpx;
    transition: all 0.3s;

    &.active {
      background: #fff;
      color: #409EFF;
      font-weight: bold;
      box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.06);
    }
  }
}

.tab-content {
  .text-area {
    width: 100%;
    min-height: 200rpx;
    background: #f5f7fa;
    border-radius: 12rpx;
    padding: 20rpx;
    font-size: 26rpx;
    margin-bottom: 20rpx;
    box-sizing: border-box;
  }

  .btn-row {
    display: flex;
    gap: 16rpx;

    button { flex: 1; }
  }
}

.upload-area {
  text-align: center;
  padding: 60rpx 20rpx;
  background: #f5f7fa;
  border-radius: 12rpx;
  border: 2rpx dashed #dcdfe6;
  margin-bottom: 20rpx;

  .upload-icon { font-size: 60rpx; display: block; margin-bottom: 12rpx; }
  .upload-text { font-size: 28rpx; color: #606266; }
  .upload-hint { font-size: 22rpx; color: #c0c4cc; margin-top: 8rpx; display: block; }
}

.file-list {
  margin-bottom: 20rpx;

  .file-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16rpx;
    background: #f5f7fa;
    border-radius: 8rpx;
    margin-bottom: 8rpx;

    .file-name {
      font-size: 26rpx;
      color: #303133;
      flex: 1;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .file-remove {
      font-size: 28rpx;
      color: #F56C6C;
      padding: 8rpx;
    }
  }
}

// 指标列表
.count-tag {
  font-size: 22rpx;
  color: #909399;
  background: #f5f7fa;
  padding: 4rpx 16rpx;
  border-radius: 20rpx;
}

.metric-row {
  position: relative;
  background: #fafafa;
  border-radius: 12rpx;
  padding: 20rpx;
  margin-bottom: 16rpx;

  .metric-picker {
    font-size: 28rpx;
    color: #409EFF;
    padding: 12rpx 16rpx;
    background: #fff;
    border-radius: 8rpx;
    margin-bottom: 12rpx;
  }

  .metric-input {
    height: 72rpx;
    background: #fff;
    border-radius: 8rpx;
    padding: 0 16rpx;
    font-size: 28rpx;
    margin-bottom: 12rpx;

    &.number { width: 180rpx; }
    &.unit { width: 120rpx; }
    &.half { width: 120rpx; }
  }

  .metric-value-row {
    margin-bottom: 12rpx;

    .metric-unit-text {
      margin-left: 12rpx;
      font-size: 24rpx;
      color: #909399;
      background: #f5f7fa;
      padding: 4rpx 12rpx;
      border-radius: 6rpx;
    }
  }

  .range-row {
    display: flex;
    align-items: center;
    gap: 8rpx;
    margin-bottom: 12rpx;

    .range-sep {
      color: #c0c4cc;
    }
  }

  .btn-icon.delete {
    position: absolute;
    top: 12rpx;
    right: 12rpx;
    padding: 4rpx 12rpx;
    background: transparent;
    font-size: 28rpx;
    border: none;
    line-height: 1;

    &::after { border: none; }
  }
}

.btn-add {
  width: 100%;
  height: 72rpx;
  line-height: 72rpx;
  border: 2rpx dashed #dcdfe6;
  border-radius: 12rpx;
  background: transparent;
  color: #909399;
  font-size: 26rpx;
  text-align: center;

  &::after { border: none; }
}

// 通用按钮
.btn-primary {
  width: 100%;
  height: 80rpx;
  line-height: 80rpx;
  background: linear-gradient(135deg, #409EFF, #66b1ff);
  color: #fff;
  font-size: 28rpx;
  border-radius: 40rpx;
  border: none;
  margin-top: 12rpx;

  &::after { border: none; }
}

.btn-secondary {
  width: 100%;
  height: 80rpx;
  line-height: 80rpx;
  background: #fff;
  color: #409EFF;
  font-size: 28rpx;
  border-radius: 40rpx;
  border: 2rpx solid #409EFF;
  margin-top: 12rpx;

  &::after { border: none; }
}

.save-area {
  padding: 30rpx 20rpx 60rpx;

  .btn-save {
    width: 100%;
    height: 88rpx;
    line-height: 88rpx;
    background: #67C23A;
    color: #fff;
    font-size: 32rpx;
    font-weight: bold;
    border-radius: 44rpx;
    border: none;

    &::after { border: none; }
    &:active { opacity: 0.85; }
  }
}
</style>
