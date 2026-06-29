# Health Metrics 台账

基于 FastAPI (后端) + Vue3 (前端) 的前后端分离体检指标台账系统。

## 本地开发启动

### 一键启动 (推荐)

我们在项目根目录提供了便捷的启动脚本，可以同时启动后端 API 和前端服务：

- **Windows 用户**: 直接双击运行 `start_dev.bat`
- **跨平台/终端用户**: 运行 `python start_dev.py` (可以通过 `Ctrl+C` 一键关闭所有服务)

> **注意**：首次运行前，请确保您已经完成下方的依赖安装步骤。

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

4. **更新代码 (Git Pull 后如何更新项目)**：
如果您在 1Panel 上通过 Git Pull 更新了代码，由于代码可能包含依赖变更或前端打包变更，您需要重新构建镜像并重启容器。请在终端执行以下命令：
```bash
docker-compose down
docker-compose up -d --build
```
> **注意**：由于挂载了 `./database` 目录，您的所有体检数据都会被安全保留，无需担心丢失。
