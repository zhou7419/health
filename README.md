# health

体检指标管理台账（多人版）：支持人员管理、指标定义（单位/参考区间）、批量录入（JSON/AI 解析）、趋势图表与健康建议。

## 启动

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 配置环境变量

复制 `.env.example` 为 `.env`，并填写 `DEEPSEEK_API_KEY`。

3. 启动

```bash
uvicorn app.main:app --reload --port 8000
```

打开：`http://127.0.0.1:8000/`
