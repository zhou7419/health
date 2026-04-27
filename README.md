# Health Metrics 台账

基于 FastAPI + SQLite + SQLAlchemy + Pydantic 的体检指标台账系统，支持多人员、指标定义（单位/参考区间）、批量录入、趋势分析、智能解析与健康建议生成。

## 启动

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 配置环境变量

复制 `.env.example` 为 `.env`，并填写 `DEEPSEEK_API_KEY`。

3. 启动服务

```bash
uvicorn app.main:app --reload --port 8000
```

打开：
- Web 界面：`http://127.0.0.1:8000/`
- API 文档：`http://127.0.0.1:8000/docs`

