# TradeReview Pro · 盘后

AI增强交易复盘系统 — 每日复盘 + AI苏格拉底审讯 + 三框架公众号文章生成

## 项目结构

```
tradereview/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/
│   │   │   └── daily_review.py     # 每日复盘路由
│   │   ├── core/
│   │   │   ├── config.py           # 配置（读取.env）
│   │   │   └── database.py         # SQLite异步连接
│   │   ├── models/
│   │   │   └── daily_review.py     # 数据模型（SQLAlchemy）
│   │   ├── schemas/
│   │   │   └── daily_review.py     # 请求/响应Schema（Pydantic）
│   │   ├── services/
│   │   │   ├── review_service.py   # 复盘CRUD业务逻辑
│   │   │   └── ai_service.py       # Kimi API调用（搜索+文章生成）
│   │   └── main.py                 # FastAPI入口
│   ├── .env                        # API Key配置（不提交git）
│   └── requirements.txt
│
├── frontend/                   # Vue3 前端
│   ├── src/
│   │   ├── api/
│   │   │   └── review.ts           # axios API封装
│   │   ├── stores/
│   │   │   └── review.ts           # Pinia状态管理
│   │   ├── views/
│   │   │   └── DailyReviewView.vue # 每日复盘主页面
│   │   ├── components/review/
│   │   │   ├── MarketSection.vue   # 一、盘面梳理
│   │   │   ├── IndustrySection.vue # 二、产业信息+AI搜索
│   │   │   └── OperationSection.vue# 三、操作复盘
│   │   ├── router/index.ts
│   │   ├── App.vue                 # 主布局（侧边栏）
│   │   └── main.ts
│   ├── index.html
│   ├── vite.config.ts
│   └── package.json
│
└── start.sh                    # 一键启动脚本

```

## 启动方式

### 1. 配置 API Key

```bash
cp backend/.env.example backend/.env
# 编辑 .env，填入 KIMI_API_KEY
```

### 2. 创建并激活虚拟环境

```bash
cd backend
# 创建虚拟环境（仅需执行一次）
python -m venv venv
# Windows 激活
venv\Scripts\activate
# macOS/Linux 激活
source venv/bin/activate
```

### 3. 安装后端依赖

```bash
pip install -r requirements.txt
```

### 3. 安装前端依赖

```bash
cd frontend
npm install
```

### 4. 启动

```bash
# 方式一：一键启动
bash start.sh

# 方式二：分别启动
# 后端
cd backend && uvicorn app.main:app --reload --port 8000
# 前端
cd frontend && npm run dev
```

访问 http://localhost:5173 → 每日复盘页面

## 当前已实现

- [x] 每日复盘完整模块（盘面梳理 + 产业信息 + 操作复盘）
- [x] AI产业信息搜索（Kimi web_search）
- [x] 三框架文章生成（散户共鸣 / 方法论 / 认知反思）
- [x] SQLite持久化存储
- [x] 按日期唯一的复盘记录（upsert）

## 待开发

- [ ] 仪表台（Dashboard）
- [ ] 每日计划
- [ ] 录入交易 + 入场逻辑时间锁
- [ ] AI苏格拉底审讯室
- [ ] 数据看板（情绪热力图、策略雷达图）
- [ ] 历史记录
- [ ] 公众号草稿箱推送（ScriptCat方案）

## 技术栈

| 层次 | 技术 |
|------|------|
| 前端 | Vue3 + ElementPlus + Pinia + Vite |
| 后端 | FastAPI + SQLAlchemy(async) + SQLite |
| AI   | Kimi API (moonshot-v1-32k) + web_search |
| 发布 | 本地运行，后续迁移腾讯云 |
