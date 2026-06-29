<template>
  <div class="page-container">
    <div class="toolbar">
      <h3>人员管理</h3>
      <el-button type="primary" @click="openPersonDialog">新增人员</el-button>
    </div>

    <el-table :data="persons" border style="width: 100%">
      <el-table-column prop="id" label="ID" width="80"></el-table-column>
      <el-table-column prop="name" label="姓名" width="200"></el-table-column>
      <el-table-column prop="gender" label="性别" width="100"></el-table-column>
      <el-table-column prop="created_at" label="创建时间"></el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="scope">
          <el-popconfirm title="确定要删除吗？该人员的所有体检记录将被清空！" @confirm="handleDeletePerson(scope.row)">
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
        @current-change="fetchPersons"
        @size-change="handleSizeChange"
      />
    </div>

    <!-- 新增人员弹窗 -->
    <el-dialog v-model="personDialogVisible" title="新增人员" width="400px">
      <el-form :model="personForm" label-width="100px">
        <el-form-item label="姓名" required>
          <el-input v-model="personForm.name"></el-input>
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="personForm.gender">
            <el-radio label="男">男</el-radio>
            <el-radio label="女">女</el-radio>
            <el-radio label="其他">其他</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="personDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPerson" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../utils/api'

const persons = ref([])
const personDialogVisible = ref(false)
const submitting = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const personForm = reactive({ name: '', gender: '' })

const fetchPersons = async () => {
  try {
    const res = await api.get('/persons/', {
      params: { page: currentPage.value, page_size: pageSize.value }
    })
    persons.value = res.data.items
    total.value = res.data.total
  } catch (error) {}
}

const handleSizeChange = () => {
  currentPage.value = 1
  fetchPersons()
}

const openPersonDialog = () => {
  personForm.name = ''
  personForm.gender = ''
  personDialogVisible.value = true
}

const submitPerson = async () => {
  if (!personForm.name) return ElMessage.warning('请输入姓名')
  submitting.value = true
  try {
    await api.post('/persons/', personForm)
    ElMessage.success('新增成功')
    personDialogVisible.value = false
    fetchPersons()
  } catch (e) {
    ElMessage.error('新增失败，可能是姓名重复')
  } finally {
    submitting.value = false
  }
}

const handleDeletePerson = async (row) => {
  try {
    await api.delete(`/persons/${row.id}`)
    ElMessage.success('删除成功')
    fetchPersons()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  fetchPersons()
})
</script>

<style scoped>
.page-container { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05); min-height: calc(100vh - 140px); }
.toolbar { margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
.pagination-wrapper { margin-top: 20px; display: flex; justify-content: flex-end; }
</style>