# Health Metrics 台账

基于 FastAPI (后端) + Vue3 (前端) 的前后端分离体检指标台账系统。支持多人员、多指标管理，AI 智能解析体检报告，趋势分析图表，AI 健康建议生成。

## 功能一览

| 模块 | 功能 |
|------|------|
| 📊 **数据概览** | 仪表盘统计卡片、人员记录排行 |
| 📋 **数据台账** | 体检记录浏览、筛选搜索、分页、CSV导出、批量删除 |
| ✏️ **批量录入** | 手动录入 / JSON解析 / AI智能解析 / 文件上传 / CSV导入，录入前预览确认 |
| 👤 **人员管理** | 人员增删、分页 |
| 📐 **指标管理** | 指标字典管理、模糊搜索、分页 |
| 📈 **趋势分析** | 多人员×多指标对比折线图、参考区间标记、滚轮缩放 |
| 🤖 **健康建议** | AI 生成健康报告（基于DeepSeek），自动保存历史记录 |
| 💾 **数据备份** | 数据库下载备份、上传恢复 |

## 技术栈

| 层 | 技术 |
|----|------|
| 后端框架 | Python FastAPI |
| 数据库 | SQLite + SQLAlchemy ORM |
| 前端框架 | Vue 3 + Vite + Element Plus |
| 图表 | ECharts |
| AI | DeepSeek API（自然语言解析 + 健康建议） |
| 部署 | Docker Compose / 1Panel |
| 移动端 | uni-app（HBuilderX，支持 Android/iOS/小程序） |

## 本地开发启动

### 前置准备

```bash
# 后端
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY、SECRET_KEY、ADMIN_PASSWORD

# 前端
cd web
npm install
```

### 一键启动

- **Windows**: 双击 `start_dev.bat`
- **跨平台**: `python start_dev.py`

### 手动启动

```bash
# 终端1 - 后端
cd backend
uvicorn app.main:app --reload --port 8000
# 访问 http://127.0.0.1:8000/docs

# 终端2 - 前端
cd web
npm run dev
# 访问 http://localhost:5173
```

### 默认账号

```
用户名: admin
密码: zhouyou123
```

## Docker 部署

```bash
# 首次部署
git clone https://github.com/zhou7419/health.git
cd health
docker compose up -d --build

# 更新代码后重建
git pull
docker compose build --no-cache
docker compose up -d

# 访问 http://服务器IP:8080
```

## 自动部署

本项目配置了 GitHub Actions 自动部署（`push main` 后触发）：

1. GitHub 自动 SSH 到服务器
2. 执行 `git pull` 拉取最新代码
3. 执行 `docker compose build --no-cache`
4. 执行 `docker compose up -d`

需要在 GitHub 仓库 **Settings → Secrets → Actions** 配置：

| Secret | 说明 |
|--------|------|
| `SSH_HOST` | 服务器 IP |
| `SSH_PORT` | SSH 端口（默认22） |
| `SSH_USER` | 登录用户名 |
| `SSH_KEY` | SSH 私钥内容 |
| `DEPLOY_PATH` | 项目路径，如 `/root/health` |

## 项目结构

```
health/
├── backend/          # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/    # API 路由
│   │   ├── crud/      # 数据库操作
│   │   ├── models/    # 数据模型
│   │   ├── schemas/   # Pydantic 模式
│   │   └── utils/     # 工具函数
│   └── Dockerfile
├── web/              # Vue3 前端
│   ├── src/views/     # 页面组件
│   └── Dockerfile
├── m/                # uni-app 移动端
├── docker-compose.yml
└── start_dev.bat
```
