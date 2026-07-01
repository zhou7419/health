<template>
  <el-container style="height: 100vh;">
    <el-header>
      <el-icon class="logo"><DataBoard /></el-icon>
      个人体检指标管理台账
      <div style="margin-left: auto; display: flex; align-items: center; gap: 10px; padding-right: 10px;">
        <el-tag type="success" effect="dark">已登录：{{ authUser || 'admin' }}</el-tag>
        <el-button size="small" @click="logout">退出登录</el-button>
      </div>
    </el-header>

    <el-container>
      <el-aside width="220px">
        <el-menu :default-active="activeMenu" class="el-menu-vertical" router>
          <el-menu-item index="/">
            <el-icon><Odometer /></el-icon>
            <span>数据概览</span>
          </el-menu-item>
          <el-menu-item index="/ledger">
            <el-icon><Document /></el-icon>
            <span>数据台账</span>
          </el-menu-item>
          <el-menu-item index="/input">
            <el-icon><Edit /></el-icon>
            <span>批量录入</span>
          </el-menu-item>
          <el-menu-item index="/persons">
            <el-icon><User /></el-icon>
            <span>人员管理</span>
          </el-menu-item>
          <el-menu-item index="/definitions">
            <el-icon><Setting /></el-icon>
            <span>指标管理</span>
          </el-menu-item>
          <el-menu-item index="/analysis">
            <el-icon><TrendCharts /></el-icon>
            <span>趋势分析</span>
          </el-menu-item>
          <el-menu-item index="/advice">
            <el-icon><FirstAidKit /></el-icon>
            <span>健康建议</span>
          </el-menu-item>
          <el-menu-item v-if="authUser === 'admin'" index="/backup">
            <el-icon><Download /></el-icon>
            <span>数据备份</span>
          </el-menu-item>
          <el-menu-item v-if="authUser === 'admin'" index="/test">
            <el-icon><Tools /></el-icon>
            <span>系统诊断</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-main>
        <router-view></router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { DataBoard, Document, Edit, User, Setting, TrendCharts, FirstAidKit, Odometer, Download, Tools } from '@element-plus/icons-vue'
import api from '../utils/api'

const route = useRoute()
const router = useRouter()
const authUser = ref('')

const activeMenu = computed(() => {
  return route.path
})

const logout = () => {
  localStorage.removeItem('access_token')
  router.push('/login')
}

onMounted(async () => {
  try {
    const res = await api.get('/auth/me')
    authUser.value = res.data.username || 'admin'
  } catch (e) {
    authUser.value = 'admin'
  }
})
</script>

<style scoped>
.el-header {
  background-color: #409EFF;
  color: white;
  line-height: 60px;
  font-size: 20px;
  font-weight: bold;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
}
.el-header .logo { margin-right: 10px; font-size: 24px; }
.el-aside { background-color: #fff; box-shadow: 2px 0 4px rgba(0, 0, 0, 0.05); z-index: 10; }
.el-menu-vertical { border-right: none; height: 100%; }
.el-main { padding: 20px; }
</style>
