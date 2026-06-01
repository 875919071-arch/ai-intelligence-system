# AI Intelligence System

小型可扩展的 **AI 智能内核**：工作记忆、工具注册表、与 OpenAI 兼容的 LLM 客户端，由 FastAPI 暴露 HTTP 接口。

## 快速开始

```bash
cd ai-intelligence-system
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env
# 编辑 .env：填入 OPENAI_API_KEY 与可选的 OPENAI_BASE_URL / OPENAI_MODEL
uvicorn ai_intelligence.app:app --reload --app-dir src
```

- 健康检查：`GET http://127.0.0.1:8000/health`
- 对话：`POST http://127.0.0.1:8000/v1/intelligence/query`，JSON：`{"message": "你好", "session_id": "可选"}`

未配置 API Key 时，内核使用本地 echo 模式，便于联调结构与工具链。

## 一日三餐选择助手

本仓库也包含一个轻量 Web MVP，用来根据口味、忌口、健康目标、预算和用餐方式推荐今日早餐、午餐、晚餐。

启动后端：

```bash
uvicorn ai_intelligence.app:app --reload --app-dir src
```

打开页面：

```text
http://127.0.0.1:8000/meal-picker/
```

可直接调用 API：

- `POST http://127.0.0.1:8000/v1/meals/recommend-day`：生成今日三餐。
- `POST http://127.0.0.1:8000/v1/meals/swap`：替换某一餐。

示例请求：

```json
{
  "preferred_cuisines": ["中式", "轻食"],
  "flavor_preferences": ["清爽", "省事"],
  "avoid_ingredients": ["海鲜"],
  "health_goal": "balanced",
  "budget": "medium",
  "dining_mode": "any",
  "prefer_quick": true
}
```

## 结构

- `src/ai_intelligence/kernel.py` — `IntelligenceKernel` 编排
- `src/ai_intelligence/memory/` — 会话级工作记忆
- `src/ai_intelligence/tools/` — 工具注册与执行
- `src/ai_intelligence/providers/` — LLM 调用
- `src/ai_intelligence/app.py` — FastAPI 应用
- `src/ai_intelligence/domain/meals.py` — 三餐推荐规则与内置候选库
- `apps/meal-picker/` — 一日三餐选择助手静态页

## 贪吃蛇（静态页）

- 本地打开：`games/snake.html`（用浏览器打开即可）。
- 推到 GitHub 后，若开启 **GitHub Pages**（分支 `main`，文件夹 `/ (root)`），试玩地址为：  
  `https://<你的用户名>.github.io/<仓库名>/games/snake.html`
