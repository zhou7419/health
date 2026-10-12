<template>
  <div class="page-container">
    <div class="toolbar">
      <h3>体检指标字典库</h3>
      <div class="toolbar-right">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索指标名称"
          clearable
          style="width: 250px; margin-right: 12px;"
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        />
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button type="primary" @click="openDefDialog()">新增指标定义</el-button>
        <el-button type="warning" :loading="detectLoading" @click="handleDetectSynonyms" style="margin-left: 8px;">
          <el-icon style="margin-right: 4px;"><Search /></el-icon>检测同义指标
        </el-button>
      </div>
    </div>

    <el-table :data="definitions" border style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="80"></el-table-column>
      <el-table-column prop="name" label="指标名称" width="200"></el-table-column>
      <el-table-column prop="unit" label="单位" width="120"></el-table-column>
      <el-table-column label="期望最小值" width="150">
        <template #default="scope">{{ scope.row.expected_min != null ? scope.row.expected_min : '-' }}</template>
      </el-table-column>
      <el-table-column label="期望最大值" width="150">
        <template #default="scope">{{ scope.row.expected_max != null ? scope.row.expected_max : '-' }}</template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="scope">
          <el-button size="small" type="primary" link @click="openDefDialog(scope.row)">编辑</el-button>
          <el-popconfirm title="确定要删除吗？将级联删除相关记录！" @confirm="handleDeleteDef(scope.row)">
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
        @current-change="fetchDefinitions"
        @size-change="handleSizeChange"
      />
    </div>

    <!-- 指标定义弹窗 -->
    <el-dialog v-model="defDialogVisible" :title="defForm.id ? '编辑指标' : '新增指标'" width="400px">
      <el-form :model="defForm" label-width="100px">
        <el-form-item label="指标名称" required>
          <el-input v-model="defForm.name"></el-input>
        </el-form-item>
        <el-form-item label="单位">
          <el-input v-model="defForm.unit" placeholder="如 kg, mmHg"></el-input>
        </el-form-item>
        <el-form-item label="期望最小值">
          <el-input-number v-model="defForm.expected_min" :controls="false" style="width: 100%;"></el-input-number>
        </el-form-item>
        <el-form-item label="期望最大值">
          <el-input-number v-model="defForm.expected_max" :controls="false" style="width: 100%;"></el-input-number>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="defDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitDef" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>

    <!-- 同义指标检测弹窗 -->
    <el-dialog v-model="synonymDialogVisible" title="检测到同义指标" width="750px" :close-on-click-modal="false">
      <template v-if="synonymSuggestions.length === 0 && !detectLoading">
        <el-empty description="未检测到同义指标" />
      </template>

      <template v-if="synonymSuggestions.length > 0">
        <el-alert
          title="以下是指标含义相同但名称不同的项目，请勾选需要合并的项后点击「确认修改」。改名后原指标的数据将合并到目标指标中。"
          type="info"
          show-icon
          :closable="false"
          style="margin-bottom: 16px;"
        />

        <el-table :data="synonymSuggestions" border style="width: 100%" max-height="400">
          <el-table-column width="55">
            <template #header>
              <el-checkbox v-model="checkAll" @change="handleCheckAllChange" />
            </template>
            <template #default="scope">
              <el-checkbox v-model="scope.row.checked" @change="handleCheckChange" />
            </template>
          </el-table-column>
          <el-table-column prop="name" label="当前名称" width="180">
            <template #default="scope">
              <el-tag type="warning">{{ scope.row.name }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="60">
            <template #default>
              <el-icon><ArrowRight /></el-icon>
            </template>
          </el-table-column>
          <el-table-column prop="target_name" label="建议改名" width="180">
            <template #default="scope">
              <el-tag type="success">{{ scope.row.target_name }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="reason" label="原因" min-width="200" />
        </el-table>
      </template>

      <template #footer>
        <el-button @click="synonymDialogVisible = false">关闭</el-button>
        <el-button
          v-if="synonymSuggestions.length > 0"
          type="primary"
          :loading="applyLoading"
          :disabled="checkedCount === 0"
          @click="handleApplyRename"
        >
          确认修改（{{ checkedCount }}项）
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, ArrowRight } from '@element-plus/icons-vue'
import api from '../utils/api'

const definitions = ref([])
const loading = ref(false)
const defDialogVisible = ref(false)
const submitting = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchKeyword = ref('')
const defForm = reactive({
  id: null,
  name: '',
  unit: '',
  expected_min: undefined,
  expected_max: undefined
})

// 同义指标检测相关
const detectLoading = ref(false)
const synonymDialogVisible = ref(false)
const synonymSuggestions = ref([])
const applyLoading = ref(false)
const checkAll = ref(true)

const checkedCount = computed(() => {
  return synonymSuggestions.value.filter(s => s.checked).length
})

const fetchDefinitions = async () => {
  loading.value = true
  try {
    const res = await api.get('/definitions/', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value,
        name: searchKeyword.value || undefined
      }
    })
    definitions.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    ElMessage.error('获取指标列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchDefinitions()
}

const handleSizeChange = () => {
  currentPage.value = 1
  fetchDefinitions()
}

const openDefDialog = (row = null) => {
  if (row) {
    defForm.id = row.id
    defForm.name = row.name
    defForm.unit = row.unit
    defForm.expected_min = row.expected_min
    defForm.expected_max = row.expected_max
  } else {
    defForm.id = null
    defForm.name = ''
    defForm.unit = ''
    defForm.expected_min = undefined
    defForm.expected_max = undefined
  }
  defDialogVisible.value = true
}

const submitDef = async () => {
  if (!defForm.name) return ElMessage.warning('请输入指标名称')
  submitting.value = true

  const payload = {
    name: defForm.name,
    unit: defForm.unit || null,
    expected_min: defForm.expected_min,
    expected_max: defForm.expected_max
  }

  try {
    if (defForm.id) {
      await api.put(`/definitions/${defForm.id}`, payload)
      ElMessage.success('更新成功')
    } else {
      await api.post('/definitions/', payload)
      ElMessage.success('新增成功')
    }
    defDialogVisible.value = false
    fetchDefinitions()
  } catch (error) {
    ElMessage.error(defForm.id ? '更新失败' : '新增失败，可能是名称重复')
  } finally {
    submitting.value = false
  }
}

const handleDeleteDef = async (row) => {
  try {
    await api.delete(`/definitions/${row.id}`)
    ElMessage.success('删除成功')
    fetchDefinitions()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

// 检测同义指标
const handleDetectSynonyms = async () => {
  detectLoading.value = true
  try {
    const res = await api.post('/smart/detect-synonyms')
    const suggestions = res.data.suggestions || []

    // 为每条建议添加 checked 标记，默认选中
    synonymSuggestions.value = suggestions.map(s => ({
      ...s,
      checked: true
    }))
    checkAll.value = true

    if (suggestions.length === 0) {
      ElMessage.info('未检测到同义指标，所有指标名称都是唯一的')
    }

    synonymDialogVisible.value = true
  } catch (error) {
    const msg = error.response?.data?.detail || '检测失败，请检查 DeepSeek API 配置'
    ElMessage.error(msg)
  } finally {
    detectLoading.value = false
  }
}

const handleCheckAllChange = (val) => {
  synonymSuggestions.value.forEach(s => {
    s.checked = val
  })
}

const handleCheckChange = () => {
  const allChecked = synonymSuggestions.value.every(s => s.checked)
  const noneChecked = synonymSuggestions.value.every(s => !s.checked)
  if (allChecked) {
    checkAll.value = true
  } else if (noneChecked) {
    checkAll.value = false
  } else {
    checkAll.value = false
  }
}

// 确认修改
const handleApplyRename = async () => {
  const selected = synonymSuggestions.value.filter(s => s.checked)
  if (selected.length === 0) {
    ElMessage.warning('请至少选择一项')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要将选中的 ${selected.length} 项指标进行改名/合并吗？此操作不可撤销！`,
      '确认修改',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
  } catch {
    return // 用户取消
  }

  applyLoading.value = true
  try {
    const renames = selected.map(s => ({
      name: s.name,
      target_name: s.target_name
    }))
    const res = await api.post('/smart/apply-rename', { renames })

    const results = res.data.results || []
    const successCount = results.filter(r => r.success).length
    const failCount = results.filter(r => !r.success).length

    // 显示详细结果
    const detailMsg = results.map(r => {
      if (r.success) {
        if (r.action === 'merged') return `✅ ${r.name} → ${r.target_name}（已合并）`
        if (r.action === 'renamed') return `✅ ${r.name} → ${r.target_name}（已改名）`
        if (r.action === 'skipped') return `⏭️ ${r.name} → ${r.target_name}（无需变更）`
        return `✅ ${r.name} → ${r.target_name}`
      } else {
        return `❌ ${r.name} → ${r.target_name}：${r.error || '失败'}`
      }
    }).join('\n')

    ElMessageBox.alert(detailMsg, `执行完成（成功${successCount}项${failCount > 0 ? `，失败${failCount}项` : ''}）`, {
      confirmButtonText: '确定',
      type: failCount > 0 ? 'warning' : 'success'
    })

    synonymDialogVisible.value = false
    // 刷新指标列表
    fetchDefinitions()
  } catch (error) {
    const msg = error.response?.data?.detail || '修改失败'
    ElMessage.error(msg)
  } finally {
    applyLoading.value = false
  }
}

onMounted(() => {
  fetchDefinitions()
})
</script>

<style scoped>
.page-container { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05); min-height: calc(100vh - 140px); }
.toolbar { margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
.toolbar-right { display: flex; align-items: center; }
.pagination-wrapper { margin-top: 20px; display: flex; justify-content: flex-end; }
</style>