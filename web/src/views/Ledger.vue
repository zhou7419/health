<template>
  <div class="page-container">
    <div class="toolbar">
      <div class="filters">
        <el-select v-model="filterPersonId" placeholder="筛选人员" clearable filterable style="width: 150px; margin-right: 10px;">
          <el-option v-for="p in persons" :key="p.id" :label="p.name" :value="p.id"></el-option>
        </el-select>
        <el-date-picker v-model="filterDate" type="date" placeholder="选择体检日期" value-format="YYYY-MM-DD" style="margin-right: 10px;" clearable></el-date-picker>
        <el-select v-model="filterMetricId" placeholder="筛选指标" clearable filterable style="width: 180px; margin-right: 10px;">
          <el-option v-for="def in definitions" :key="def.id" :label="def.name" :value="def.id"></el-option>
        </el-select>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleExport">导出 CSV</el-button>
        <el-popconfirm
          v-if="selectedIds.length > 0"
          title="确定要删除选中的记录吗？"
          @confirm="handleBatchDelete"
        >
          <template #reference>
            <el-button type="danger" plain>批量删除 ({{ selectedIds.length }})</el-button>
          </template>
        </el-popconfirm>
        <el-popconfirm v-if="filterDate" :title="`确定要删除 ${filterDate} 的所有体检记录吗？`" @confirm="handleDeleteByDate">
          <template #reference>
            <el-button type="danger" plain>删除该日记录</el-button>
          </template>
        </el-popconfirm>
      </div>
      <el-button type="primary" @click="$router.push('/input')">
        <el-icon style="margin-right: 5px;"><Plus /></el-icon> 新增记录
      </el-button>
    </div>

    <el-table :data="records" border style="width: 100%" v-loading="loading" @selection-change="onSelectionChange">
      <el-table-column type="selection" width="45" />
      <el-table-column prop="record_date" label="体检日期" width="120" sortable></el-table-column>
      <el-table-column label="人员" width="100">
        <template #default="scope">{{ scope.row.person.name }}</template>
      </el-table-column>
      <el-table-column label="指标名称" width="150">
        <template #default="scope">{{ scope.row.metric.name }}</template>
      </el-table-column>
      <el-table-column label="数值" width="150">
        <template #default="scope">
          <span :class="getValueClass(scope.row.value, scope.row.metric)">
            {{ scope.row.value }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="期望区间" width="150">
        <template #default="scope">
          {{ formatExpectedRange(scope.row.metric) }}
        </template>
      </el-table-column>
      <el-table-column label="单位" width="100">
        <template #default="scope">{{ scope.row.metric.unit }}</template>
      </el-table-column>
      <el-table-column prop="notes" label="备注"></el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="scope">
          <el-button size="small" type="primary" link @click="handleEditRecord(scope.row)">编辑</el-button>
          <el-popconfirm title="确定要删除这条记录吗？" @confirm="handleDeleteRecord(scope.row)">
            <template #reference>
              <el-button size="small" type="danger" link>删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="fetchRecords"
        @size-change="handleSizeChange"
      />
    </div>

    <!-- 编辑记录弹窗 -->
    <el-dialog v-model="editRecordDialogVisible" title="编辑体检记录" width="400px">
      <el-form v-if="editRecordForm" :model="editRecordForm" label-width="100px">
        <el-form-item label="人员">
          <span>{{ editRecordForm.person_name }}</span>
        </el-form-item>
        <el-form-item label="指标">
          <span>{{ editRecordForm.metric_name }}</span>
        </el-form-item>
        <el-form-item label="体检日期" required>
          <el-date-picker v-model="editRecordForm.record_date" type="date" value-format="YYYY-MM-DD" style="width: 100%;"></el-date-picker>
        </el-form-item>
        <el-form-item label="数值" required>
          <el-input-number v-model="editRecordForm.value" :controls="false" style="width: 100%;"></el-input-number>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="editRecordForm.notes"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editRecordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEditRecord" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '../utils/api'

const records = ref([])
const persons = ref([])
const definitions = ref([])
const loading = ref(false)
const submitting = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const selectedIds = ref([])
const filterDate = ref('')
const filterPersonId = ref('')
const filterMetricId = ref('')

const editRecordDialogVisible = ref(false)
const editRecordForm = ref(null)

const fetchRecords = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (filterDate.value) params.record_date = filterDate.value
    if (filterMetricId.value) params.metric_id = filterMetricId.value
    if (filterPersonId.value) params.person_id = filterPersonId.value

    const res = await api.get('/metrics/', { params })
    records.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    ElMessage.error('获取台账数据失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchRecords()
}

const handleExport = () => {
  const params = {}
  if (filterDate.value) params.record_date = filterDate.value
  if (filterMetricId.value) params.metric_id = filterMetricId.value
  if (filterPersonId.value) params.person_id = filterPersonId.value

  const query = new URLSearchParams(params).toString()
  window.open(`/api/v1/metrics/export?${query}`, '_blank')
}

const handleSizeChange = () => {
  currentPage.value = 1
  fetchRecords()
}

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

const formatExpectedRange = (metric) => {
  if (metric.expected_min != null && metric.expected_max != null) return `${metric.expected_min} - ${metric.expected_max}`
  if (metric.expected_min != null) return `≥ ${metric.expected_min}`
  if (metric.expected_max != null) return `≤ ${metric.expected_max}`
  return '-'
}

const getValueClass = (value, metric) => {
  if (metric.expected_min != null && value < metric.expected_min) return 'abnormal-value'
  if (metric.expected_max != null && value > metric.expected_max) return 'abnormal-value'
  return 'normal-value'
}

const onSelectionChange = (selection) => {
  selectedIds.value = selection.map(r => r.id)
}

const handleBatchDelete = async () => {
  try {
    const res = await api.post(`/metrics/batch-delete?ids=${selectedIds.value.join('&ids=')}`)
    ElMessage.success(`成功删除 ${res.data.deleted_count} 条记录`)
    selectedIds.value = []
    fetchRecords()
  } catch (e) {
    ElMessage.error('批量删除失败')
  }
}

const handleEditRecord = (row) => {
  editRecordForm.value = {
    id: row.id,
    person_name: row.person.name,
    metric_name: row.metric.name,
    record_date: row.record_date,
    value: row.value,
    notes: row.notes || ''
  }
  editRecordDialogVisible.value = true
}

const submitEditRecord = async () => {
  if (editRecordForm.value.value === null || editRecordForm.value.value === undefined) {
    return ElMessage.warning('请输入数值')
  }
  submitting.value = true
  try {
    await api.put(`/metrics/${editRecordForm.value.id}`, {
      value: editRecordForm.value.value,
      record_date: editRecordForm.value.record_date,
      notes: editRecordForm.value.notes
    })
    ElMessage.success('更新成功')
    editRecordDialogVisible.value = false
    fetchRecords()
  } catch (e) {
    ElMessage.error('更新失败')
  } finally {
    submitting.value = false
  }
}

const handleDeleteRecord = async (row) => {
  try {
    await api.delete(`/metrics/${row.id}`)
    ElMessage.success('删除成功')
    fetchRecords()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

const handleDeleteByDate = async () => {
  if (!filterDate.value) return
  try {
    let url = `/metrics/date/${filterDate.value}`
    if (filterPersonId.value) {
      url += `?person_id=${filterPersonId.value}`
    }
    const res = await api.delete(url)
    ElMessage.success(`成功删除 ${res.data.deleted_count} 条记录`)
    fetchRecords()
  } catch (e) {
    ElMessage.error('删除该日记录失败')
  }
}

onMounted(() => {
  fetchPersons()
  fetchDefinitions()
  fetchRecords()
})
</script>

<style scoped>
.page-container { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05); min-height: calc(100vh - 140px); }
.toolbar { margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
.abnormal-value { color: #F56C6C; font-weight: bold; }
.normal-value { color: #67C23A; font-weight: bold; }
.pagination-wrapper { margin-top: 20px; display: flex; justify-content: flex-end; }
</style>