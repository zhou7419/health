# Health Metrics 台账

基于 FastAPI (后端) + Vue3 (前端) 的前后端分离体检指标台账系统。

## 本地开发启动

### 1. 启动后端 (FastAPI)

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY、SECRET_KEY、ADMIN_PASSWORD
uvicorn app.main:app --reload --port 8000
```
后端 API 地址：`http://127.0.0.1:8000/docs`

### 2. 启动前端 (Vue3 + Vite)

```bash
cd web
npm install
npm run dev
```
前端访问地址：`http://localhost:5173` (具体端口看终端输出)

## 生产部署 (Docker Compose / 1Panel)

推荐使用仓库自带的 `docker-compose.yml` 进行一键部署，它包含了 `backend` 和 `web` 两个服务。

1. **准备配置文件**：确保在根目录或 1Panel 环境变量中设置以下变量：
   - `DEEPSEEK_API_KEY`
   - `SECRET_KEY`
   - `ADMIN_PASSWORD`

2. **启动**：
```bash
docker-compose up -d --build
```

3. **访问**：
通过宿主机的 `80` 端口访问系统（Nginx 会自动将 `/api` 的请求反向代理到后端的 8000 端口）。
