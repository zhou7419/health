# Health Metrics 台账

基于 FastAPI + SQLite + SQLAlchemy + Pydantic 的体检指标台账系统，支持多人员、指标定义（单位/参考区间）、批量录入、趋势分析、智能解析与健康建议生成。

## 启动

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 配置环境变量

复制 `.env.example` 为 `.env`，并填写：
- `DEEPSEEK_API_KEY`（智能解析/健康建议需要）
- `SECRET_KEY`（登录 token 签名需要）
- `ADMIN_PASSWORD`（登录密码）

3. 启动服务

```bash
uvicorn app.main:app --reload --port 8000
```

打开：
- Web 界面：`http://127.0.0.1:8000/`
- API 文档：`http://127.0.0.1:8000/docs`

## Docker

构建镜像：

```bash
docker build -t zhou7419/health:latest .
```

运行容器（本地挂载 SQLite 数据目录）：

```bash
docker run -d --name health \
  -p 8000:8000 \
  -e DATABASE_URL="sqlite:///./database/app.db" \
  -e DEEPSEEK_BASE_URL="https://api.deepseek.com" \
  -e DEEPSEEK_API_KEY="YOUR_KEY" \
  -e SECRET_KEY="YOUR_SECRET" \
  -e ADMIN_USERNAME="admin" \
  -e ADMIN_PASSWORD="YOUR_PASSWORD" \
  -v "$(pwd)/database:/app/database" \
  --restart unless-stopped \
  zhou7419/health:latest
```

## 1Panel 部署

推荐使用 Compose 部署（仓库已提供 `docker-compose.yml`）：

1. 在 1Panel 的容器/编排里新建 Compose 应用，粘贴 `docker-compose.yml` 内容
2. 把 `DEEPSEEK_API_KEY` 改成你自己的 key（不要留空）
3. 把 `SECRET_KEY` / `ADMIN_PASSWORD` 填好（否则无法登录）
4. 挂载卷保持数据持久化：把宿主机某个目录映射到容器 `/app/database`
5. 启动后通过 8000 端口访问
