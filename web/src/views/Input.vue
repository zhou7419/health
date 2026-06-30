<template>
  <div class="page-container">
    <h3>批量录入体检指标</h3>
    <el-form label-width="100px" style="max-width: 900px; margin-top: 20px;">
      <el-form-item label="人员" required>
        <el-select v-model="batchForm.person_id" placeholder="选择人员" style="width: 100%;">
          <el-option v-for="p in persons" :key="p.id" :label="p.name" :value="p.id"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="体检日期" required>
        <el-date-picker v-model="batchForm.recordDate" type="date" placeholder="选择日期" value-format="YYYY-MM-DD"></el-date-picker>
      </el-form-item>

      <el-divider>快速导入 (支持文件、JSON与智能文本)</el-divider>
      <el-form-item label="方式选择">
        <el-radio-group v-model="importType">
          <el-radio-button label="text">文本解析</el-radio-button>
          <el-radio-button label="smart_file">AI文件解析</el-radio-button>
          <el-radio-button label="file">标准CSV导入</el-radio-button>
        </el-radio-group>
      </el-form-item>

      <div v-if="importType === 'text'">
        <el-form-item label="原始数据">
          <el-input 
            v-model="jsonInput" 
            type="textarea" 
            :rows="4" 
            placeholder='支持两种方式：
1. 直接粘贴标准JSON，例如：{"体重": "70.8", "收缩压": 120}。
2. 粘贴自然语言（智能解析），例如："我今天早上称了一下体重，大概是 75.2kg，然后量了血压是 125 毫米汞柱"。'>
          </el-input>
          <div style="margin-top: 10px; text-align: right; width: 100%;">
            <el-button type="info" plain size="small" @click="parseJsonInput">标准JSON解析</el-button>
            <el-button type="primary" size="small" @click="smartParseInput" :loading="parsingText">
              <el-icon style="margin-right: 5px;"><MagicStick /></el-icon>
              AI 智能解析
            </el-button>
          </div>
        </el-form-item>
      </div>

      <div v-if="importType === 'smart_file'">
        <el-form-item label="智能解析文件">
          <el-upload
            class="upload-demo"
            drag
            action="#"
            :auto-upload="false"
            :show-file-list="true"
            :limit="10"
            multiple
            accept=".pdf,.txt,.md,.csv,.png,.jpg,.jpeg,.webp,.gif"
            :on-change="handleSmartFileChange"
            :on-exceed="handleSmartExceed"
            :file-list="smartFileList"
            :on-remove="handleSmartFileRemove"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将文件或图片拖到此处，或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持多图 (.jpg, .png)、体检报告 PDF，或纯文本文件。大模型将智能提取各项指标。
              </div>
            </template>
          </el-upload>
          <div style="margin-top: 10px; width: 100%;">
            <el-button type="primary" @click="submitSmartFileUpload" :loading="parsingText" :disabled="smartFileList.length === 0">
              <el-icon style="margin-right: 5px;"><MagicStick /></el-icon>
              开始 AI 智能解析
            </el-button>
          </div>
        </el-form-item>
      </div>

      <div v-if="importType === 'file'">
        <el-form-item label="CSV文件">
          <el-upload
            class="upload-demo"
            drag
            action="#"
            :auto-upload="false"
            :show-file-list="true"
            :limit="1"
            accept=".csv"
            :on-change="handleFileChange"
            :on-exceed="handleExceed"
            :file-list="fileList"
            :on-remove="handleFileRemove"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                只能上传 CSV 文件，请确保包含表头: 指标名称,数值,单位,参考下限,参考上限,备注
                <el-button link type="primary" style="margin-left: 10px;" @click="downloadTemplate">下载模板</el-button>
              </div>
            </template>
          </el-upload>
          <div style="margin-top: 10px; width: 100%;">
            <el-button type="primary" @click="submitFileUpload" :loading="uploading" :disabled="fileList.length === 0">
              <el-icon style="margin-right: 5px;"><Upload /></el-icon>
              确认上传并录入
            </el-button>
          </div>
        </el-form-item>
      </div>
      
      <el-divider>
        指标列表 
        <el-tag type="info" size="small" style="margin-left: 10px;">共 {{ validMetricCount }} 项待保存</el-tag>
      </el-divider>
      
      <div v-for="(metric, index) in batchForm.metrics" :key="index" style="display: flex; gap: 10px; margin-bottom: 15px; align-items: flex-start; flex-wrap: wrap;">
        <!-- 指标选择 -->
        <div style="flex: 0 0 200px;">
          <el-select v-model="metric.metric_id" placeholder="选择指标" style="width: 100%;" @change="onMetricSelectChange(metric)">
            <el-option v-for="def in definitions" :key="def.id" :label="def.name" :value="def.id"></el-option>
            <el-option label="+ 自定义 (手动填写)" value="custom" style="color: #409EFF; font-weight: bold;"></el-option>
          </el-select>
          <!-- 自定义名称 -->
          <div v-if="metric.metric_id === 'custom'" style="margin-top: 8px;">
            <el-input v-model="metric.customName" placeholder="自定义名称"></el-input>
          </div>
        </div>
        
        <el-input-number v-model="metric.value" :controls="false" placeholder="录入数值" style="flex: 0 0 120px;"></el-input-number>
        
        <!-- 期望区间展示/编辑 -->
        <div style="flex: 0 0 200px;">
          <div v-if="metric.metric_id !== 'custom' && metric.metric_id" style="line-height: 32px; color: #909399; font-size: 13px; background: #f5f7fa; padding: 0 10px; border-radius: 4px;">
            参考: {{ getExpectedRangeStr(metric.metric_id) }}
          </div>
          <div v-else style="display: flex; align-items: center; gap: 5px;">
            <el-input-number v-model="metric.expected_min" :controls="false" placeholder="参考下限" style="width: 90px;"></el-input-number>
            <span>-</span>
            <el-input-number v-model="metric.expected_max" :controls="false" placeholder="参考上限" style="width: 90px;"></el-input-number>
          </div>
        </div>

        <!-- 单位展示/编辑 -->
        <div style="flex: 0 0 100px;">
          <div v-if="metric.metric_id !== 'custom' && metric.metric_id" style="line-height: 32px; color: #909399; text-align: center; background: #f5f7fa; border-radius: 4px;">
            {{ getMetricUnit(metric.metric_id) || '无单位' }}
          </div>
          <el-input v-else v-model="metric.customUnit" placeholder="单位(选填)"></el-input>
        </div>
        
        <el-input v-model="metric.notes" placeholder="备注" style="flex: 1; min-width: 150px;"></el-input>
        
        <el-button type="danger" circle @click="removeBatchItem(index)" :disabled="batchForm.metrics.length === 1">
          <el-icon><Delete /></el-icon>
        </el-button>
      </div>
      
      <el-form-item label-width="0" style="margin-top: 20px;">
        <el-button type="info" plain @click="addBatchItem" style="width: 100%;">
          <el-icon style="margin-right: 5px;"><Plus /></el-icon> 添加一条指标
        </el-button>
      </el-form-item>
      
      <el-form-item label-width="0" style="margin-top: 30px; text-align: center;">
        <el-button type="primary" size="large" @click="previewBatch">预览并提交</el-button>
        <el-button size="large" @click="$router.push('/')">取消</el-button>
      </el-form-item>
    </el-form>
  </div>

  <!-- 数据预览弹窗 -->
  <el-dialog v-model="previewVisible" title="请确认要录入的数据" width="700px">
    <el-table :data="previewData" border max-height="400">
      <el-table-column prop="name" label="指标名称" width="150"></el-table-column>
      <el-table-column prop="value" label="数值" width="100"></el-table-column>
      <el-table-column prop="unit" label="单位" width="80"></el-table-column>
      <el-table-column prop="expected_min" label="下限" width="80">
        <template #default="scope">{{ scope.row.expected_min ?? '-' }}</template>
      </el-table-column>
      <el-table-column prop="expected_max" label="上限" width="80">
        <template #default="scope">{{ scope.row.expected_max ?? '-' }}</template>
      </el-table-column>
      <el-table-column prop="notes" label="备注" min-width="120">
        <template #default="scope">{{ scope.row.notes || '-' }}</template>
      </el-table-column>
    </el-table>
    <div style="margin-top: 12px; color: #909399; font-size: 13px;">
      人员: <b>{{ previewPersonName }}</b> &nbsp;|&nbsp; 日期: <b>{{ batchForm.recordDate }}</b> &nbsp;|&nbsp; 共 <b>{{ previewData.length }}</b> 条指标
    </div>
    <template #footer>
      <el-button @click="previewVisible = false">返回修改</el-button>
      <el-button type="primary" @click="confirmSubmit" :loading="submitting">确认提交</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { MagicStick, Plus, Delete, UploadFilled, Upload } from '@element-plus/icons-vue'
import api from '../utils/api'

const router = useRouter()
const persons = ref([])
const definitions = ref([])
const submitting = ref(false)
const parsingText = ref(false)
const uploading = ref(false)
const jsonInput = ref('')
const importType = ref('text')
const fileList = ref([])
const smartFileList = ref([])
const previewVisible = ref(false)
const previewData = ref([])
const previewPersonName = ref('')

const batchForm = reactive({
  person_id: '',
  recordDate: new Date().toISOString().split('T')[0],
  metrics: []
})

const fetchPersons = async () => {
  try {
    const res = await api.get('/persons/', { params: { page: 1, page_size: 100 } })
    persons.value = res.data.items
    if (persons.value.length > 0 && !batchForm.person_id) {
      batchForm.person_id = persons.value[0].id
    }
  } catch (error) {}
}

const fetchDefinitions = async () => {
  try {
    const res = await api.get('/definitions/', { params: { page: 1, page_size: 1000 } })
    definitions.value = res.data.items
  } catch (error) {}
}

const addBatchItem = () => {
  batchForm.metrics.push({
    metric_id: '',
    customName: '',
    customUnit: '',
    expected_min: undefined,
    expected_max: undefined,
    value: undefined,
    notes: ''
  })
}

const removeBatchItem = (index) => {
  batchForm.metrics.splice(index, 1)
}

const validMetricCount = computed(() => {
  return batchForm.metrics.filter(m => {
    if (m.value === undefined || m.value === null) return false
    if (m.metric_id === 'custom') return !!m.customName
    return !!m.metric_id
  }).length
})

const getMetricUnit = (id) => {
  if (id === 'custom' || !id) return ''
  const def = definitions.value.find(d => d.id === id)
  return def ? def.unit : ''
}

const getExpectedRangeStr = (id) => {
  if (id === 'custom' || !id) return ''
  const def = definitions.value.find(d => d.id === id)
  if (!def) return ''
  if (def.expected_min != null && def.expected_max != null) return `${def.expected_min} - ${def.expected_max}`
  if (def.expected_min != null) return `≥ ${def.expected_min}`
  if (def.expected_max != null) return `≤ ${def.expected_max}`
  return '-'
}

const onMetricSelectChange = (metric) => {
  if (metric.metric_id === 'custom') {
    metric.customName = ''
    metric.customUnit = ''
    metric.expected_min = undefined
    metric.expected_max = undefined
  }
}

const appendParsedDataToForm = (dataObj) => {
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
      value: val,
      notes: ''
    }

    if (existDef) {
      newItem.metric_id = existDef.id
    } else {
      newItem.metric_id = 'custom'
      newItem.customName = key
      newItem.customUnit = unit
      newItem.expected_min = expected_min
      newItem.expected_max = expected_max
    }

    if (batchForm.metrics.length === 1 && !batchForm.metrics[0].metric_id && batchForm.metrics[0].value === undefined) {
      batchForm.metrics = [newItem]
    } else {
      batchForm.metrics.push(newItem)
    }
  }
}

const parseJsonInput = () => {
  if (!jsonInput.value.trim()) return ElMessage.warning('请输入JSON数据')
  try {
    const data = JSON.parse(jsonInput.value)
    appendParsedDataToForm(data)
    ElMessage.success('解析成功')
    jsonInput.value = ''
  } catch (error) {
    ElMessage.error('JSON格式错误，解析失败')
  }
}

const smartParseInput = async () => {
  if (!jsonInput.value.trim()) return ElMessage.warning('请输入需要解析的文本')
  parsingText.value = true
  try {
    const res = await api.post('/smart/', { text: jsonInput.value })
    appendParsedDataToForm(res.data)
    ElMessage.success('AI 解析成功')
    jsonInput.value = ''
  } catch (error) {
    const errorMsg = error.response?.data?.detail || '智能解析失败'
    ElMessage.error(errorMsg)
  } finally {
    parsingText.value = false
  }
}

const handleSmartFileChange = (file, fileList) => {
  smartFileList.value = fileList
}

const handleSmartExceed = (files) => {
  ElMessage.warning('最多只能上传 10 个文件或图片')
}

const handleSmartFileRemove = (file, fileList) => {
  smartFileList.value = fileList
}

const submitSmartFileUpload = async () => {
  if (smartFileList.value.length === 0) return ElMessage.warning('请选择文件或图片')

  const formData = new FormData()
  smartFileList.value.forEach(f => {
    const rawFile = f.raw || f
    formData.append('files', rawFile)
  })

  parsingText.value = true
  try {
    const res = await api.post('/smart/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    appendParsedDataToForm(res.data)
    ElMessage.success('文件 AI 解析成功，请检查下方指标列表')
    smartFileList.value = []
  } catch (error) {
    const errorMsg = error.response?.data?.detail || '智能解析文件失败'
    ElMessage.error(errorMsg)
  } finally {
    parsingText.value = false
  }
}

const getValidMetrics = () => {
  return batchForm.metrics.filter(m => {
    if (m.value === undefined || m.value === null) return false
    if (m.metric_id === 'custom') return !!m.customName
    return !!m.metric_id
  })
}

const buildPayload = (validMetrics) => ({
  person_id: batchForm.person_id,
  record_date: batchForm.recordDate,
  metrics: validMetrics.map(m => ({
    metric_id: m.metric_id === 'custom' ? null : m.metric_id,
    name: m.metric_id === 'custom' ? m.customName : null,
    unit: m.metric_id === 'custom' ? m.customUnit : null,
    expected_min: m.metric_id === 'custom' ? m.expected_min : null,
    expected_max: m.metric_id === 'custom' ? m.expected_max : null,
    value: m.value,
    notes: m.notes
  }))
})

const previewBatch = () => {
  if (!batchForm.person_id) return ElMessage.warning('请选择人员')
  if (!batchForm.recordDate) return ElMessage.warning('请选择体检日期')

  const validMetrics = getValidMetrics()
  if (validMetrics.length === 0) return ElMessage.warning('至少需要一条有效的指标记录')

  const person = persons.value.find(p => p.id === batchForm.person_id)
  previewPersonName.value = person ? person.name : '-'

  previewData.value = validMetrics.map(m => ({
    name: m.metric_id === 'custom' ? m.customName : (definitions.value.find(d => d.id === m.metric_id)?.name || '-'),
    value: m.value,
    unit: m.metric_id === 'custom' ? m.customUnit : (definitions.value.find(d => d.id === m.metric_id)?.unit || ''),
    expected_min: m.metric_id === 'custom' ? m.expected_min : (definitions.value.find(d => d.id === m.metric_id)?.expected_min),
    expected_max: m.metric_id === 'custom' ? m.expected_max : (definitions.value.find(d => d.id === m.metric_id)?.expected_max),
    notes: m.notes
  }))

  previewVisible.value = true
}

const confirmSubmit = async () => {
  const validMetrics = getValidMetrics()
  const payload = buildPayload(validMetrics)

  submitting.value = true
  try {
    await api.post('/metrics/batch', payload)
    ElMessage.success(`成功保存 ${validMetrics.length} 条记录`)
    previewVisible.value = false
    router.push('/')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    submitting.value = false
  }
}

const handleFileChange = (file) => {
  fileList.value = [file]
}

const handleExceed = (files) => {
  fileList.value = [files[0]]
}

const handleFileRemove = () => {
  fileList.value = []
}

const downloadTemplate = () => {
  const template = '指标名称,数值,单位,参考下限,参考上限,备注\n体重,70.5,kg,,,\n收缩压,120,mmHg,90,140,正常\n舒张压,80,mmHg,60,90,正常'
  const blob = new Blob([new Uint8Array([0xEF, 0xBB, 0xBF]), template], { type: 'text/csv;charset=utf-8' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = '体检指标导入模板.csv'
  a.click()
  window.URL.revokeObjectURL(url)
}

const submitFileUpload = async () => {
  if (!batchForm.person_id) return ElMessage.warning('请选择人员')
  if (!batchForm.recordDate) return ElMessage.warning('请选择体检日期')
  if (fileList.value.length === 0) return ElMessage.warning('请选择文件')

  const file = fileList.value[0].raw || fileList.value[0]
  if (!file) return ElMessage.warning('文件无效')

  const formData = new FormData()
  formData.append('person_id', batchForm.person_id)
  formData.append('record_date', batchForm.recordDate)
  formData.append('file', file)

  uploading.value = true
  try {
    const res = await api.post('/metrics/batch/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    ElMessage.success(`成功从文件导入 ${res.data.length} 条记录`)
    router.push('/')
  } catch (error) {
    const errorMsg = error.response?.data?.detail || '文件上传解析失败'
    ElMessage.error(errorMsg)
  } finally {
    uploading.value = false
  }
}

onMounted(() => {
  fetchPersons()
  fetchDefinitions()
  if (batchForm.metrics.length === 0) addBatchItem()
})
</script>

<style scoped>
.page-container { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05); min-height: calc(100vh - 140px); }
</style>