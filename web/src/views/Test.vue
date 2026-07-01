<template>
  <div class="page-container">
    <div class="toolbar">
      <h3>测试页面</h3>
    </div>
    <el-alert title="自动部署测试" type="success" :closable="false" show-icon>
      如果看到这个页面，说明 GitHub Actions 自动部署成功了！
    </el-alert>
    <el-card shadow="hover" style="margin-top: 20px;">
      <template #header>部署信息</template>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="部署时间">{{ deployTime }}</el-descriptions-item>
        <el-descriptions-item label="提交版本">{{ commitHash }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const deployTime = ref(new Date().toLocaleString('zh-CN'))
const commitHash = ref('未知')
</script>

<style scoped>
.page-container { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05); min-height: calc(100vh - 140px); }
.toolbar { margin-bottom: 20px; }
</style>
