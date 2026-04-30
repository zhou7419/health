<template>
  <div class="login-container">
    <div class="card">
      <div class="title">登录</div>
      <div class="sub">体检指标管理台账</div>
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户名" required>
          <el-input v-model="form.username" autocomplete="username"></el-input>
        </el-form-item>
        <el-form-item label="密码" required>
          <el-input v-model="form.password" type="password" show-password autocomplete="current-password" @keyup.enter="login"></el-input>
        </el-form-item>
        <el-form-item label-width="0">
          <el-button type="primary" style="width: 100%;" @click="login" :loading="loading">登录</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../utils/api'

const router = useRouter()
const loading = ref(false)
const form = reactive({ username: 'admin', password: '' })

const login = async () => {
  if (!form.username || !form.password) return ElMessage.warning('请输入用户名和密码')
  loading.value = true
  try {
    const res = await api.post('/auth/login', {
      username: form.username,
      password: form.password
    })
    localStorage.setItem('access_token', res.data.access_token)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (e) {
    const msg = e.response?.data?.detail || '登录失败'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container { 
  height: 100vh; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  background: radial-gradient(circle at 10% 20%, rgb(226, 240, 254) 0%, rgb(255, 255, 255) 100%);
}
.card { 
  width: 420px; 
  background: rgba(255, 255, 255, 0.9); 
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 12px; 
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07); 
  padding: 32px 24px; 
}
.title { font-size: 22px; font-weight: 700; margin-bottom: 8px; color: #303133; text-align: center; }
.sub { color: #909399; font-size: 14px; margin-bottom: 24px; text-align: center; }
</style>