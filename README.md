# RAG Knowledge Assistant

基于 RAG（检索增强生成）架构的企业知识库问答系统，集成 Function Calling 工具调用能力。

## 功能模块

| 模块 | 说明 |
|------|------|
| 智能问答 | 上传文档后提问，混合检索相关内容后由 LLM 生成答案，附来源引用和相似度评分 |
| 自由闲聊 | Function Calling 驱动：LLM 自主决定直接回答还是调用工具（天气查询、网页搜索） |
| 文档上传 | 支持 PDF / Word / PowerPoint / TXT，自动分块、向量化、建 BM25 索引 |
| 知识库管理 | 查看文档元数据（文件名、大小、分块数），支持删除 |
| 多轮对话 | 会话历史 SQLite 持久化��支持新建/切换/删除会话，AI 理解上下文和追问 |

## 架构设计

```
┌─────────────────────────────────────────────────────┐
│                      前端 (React)                    │
│   智能问答页  │  自由闲聊页  │  上传页  │  管理页    │
└──────┬──────────────┬──────────────────────────────┘
       │              │
       ▼              ▼
┌─────────────────────────────────────────────────────┐
│                   FastAPI 路由层                      │
│   /api/conversations/:id/query  │  /api/chat         │
│   /api/query   /api/upload   /api/documents          │
└──────┬──────────────┬──────────────────────────────┘
       │              │
       ▼              ▼
┌────────────┐  ┌────────────────────────────────────┐
│ RAGService │  │           AgentService             │
│            │  │   Function Calling Loop            │
│ 1.混合检索  │  │   1. LLM + TOOL_DEFINITIONS        │
│ 2.拼Prompt  │  │   2. tool_calls? → 执行工具        │
│ 3.生成答案  │  │   3. 结果喂回 → 最终答案           │
└──────┬─────┘  └───────────────┬────────────────────┘
       │                        │
       ▼                        ▼
┌─────────────┐         ┌──────────────────┐
│  VectorDB   │         │   tools/         │
│  Service    │         │  ├── weather.py  │
│             │         │  └── search.py   │
│ 向量检索     │         └──────────────────┘
│ BM25检索    │
│ RRF 融合    │
└──────┬──────┘
       │
       ▼
┌─────────────┐   ┌─────────────┐
│  ChromaDB   │   │   SQLite    │
│  向量存储    │   │  会话/消息   │
└─────────────┘   └─────────────┘
```

## 技术栈

### 后端

| 技术 | 用途 |
|------|------|
| Python 3.10 + FastAPI | 异步 Web 框架，自动生成 OpenAPI 文档 |
| 智谱 GLM-4-air | 大语言模型（生成答案、Function Calling） |
| 智谱 Embedding-3 | 向量化模型（1536 维，存储与检索必须一致） |
| ChromaDB | 本地持久化向量数据库（cosine 相似度） |
| rank-bm25 | BM25 关键词检索（中文字符级分词） |
| SQLite + SQLAlchemy 2.0 | 会话与消息持久化 |
| duckduckgo-search | 免费网页搜索（无需 API Key） |
| PyPDF2 / python-docx / python-pptx | 文档解析 |
| pydantic-settings | 环境变量配置管理 |
| loguru | 结构化日志 |

### 前端

| 技术 | 用途 |
|------|------|
| React 18 + TypeScript | UI 框架 |
| Vite | 构建工具 |
| Ant Design 5 | UI 组件库 |
| Zustand | 全局状态管理（会话列表、当前会话、消息） |
| Axios | HTTP 客户端 |
| react-markdown | 渲染 AI 回复中的 Markdown |
| React Router | 客户端路由（4 个页面） |

## 项目结构

```
Rag_AI/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes.py              # 文档/问答/闲聊/健康检查接口
│   │   │   └── conversation_routes.py # 会话管理接口
│   │   ├── core/
│   │   │   ├── rag.py                 # RAGService：纯检索增强生成
│   │   │   ├── agent.py               # AgentService：Function Calling 驱动的闲聊
│   │   │   ├── llm.py                 # LLM 封装（generate / with_tools / with_messages）
│   │   │   └── embeddings.py          # Embedding 封装
│   │   ├── tools/
│   │   │   ├── __init__.py            # 工具注册表（TOOL_DEFINITIONS + TOOL_REGISTRY）
│   │   │   ├── weather.py             # 天气工具（wttr.in）
│   │   │   └── search.py              # 网页搜索工具（DuckDuckGo）
│   │   ├── services/
│   │   │   ├── vectordb.py            # 混合检索服务（向量 + BM25 + RRF）
│   │   │   ├── document.py            # 文档处理服务
│   │   │   └── conversation.py        # 会话管理服务
│   │   ├── models/
│   │   │   ├── db_models.py           # SQLAlchemy 数据模型
│   │   │   └── schemas.py             # Pydantic 请求/响应模型
│   │   ├── utils/
│   │   │   └── file_parser.py         # 文档解析工具
│   │   ├── config.py                  # 配置管理
│   │   ├── database.py                # SQLite 连接
│   │   └── main.py                    # 应用入口
│   ├── data/
│   │   ├── uploads/                   # 上传的原始文档
│   │   ├── chroma_db/                 # ChromaDB 向量数据
│   │   └── conversations.db           # 会话记录（SQLite）
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── ChatPage.tsx           # 智能问答（含会话侧边栏）
│   │   │   ├── FreeChatPage.tsx       # 自由闲聊（支持天气/搜索工具）
│   │   │   ├── UploadPage.tsx         # 文档上传
│   │   │   └── ManagementPage.tsx     # 知识库管理
│   │   ├── components/
│   │   │   ├── Layout.tsx             # 全局布局与导航
│   │   │   └── ConversationSidebar.tsx
│   │   ├── services/api.ts            # 所有 API 调用封装
│   │   ├── conversationStore.ts       # Zustand 会话状态
│   │   ├── types/api.ts               # TypeScript 接口定义
│   │   └── App.tsx                    # 路由配置
│   └── package.json
└── README.md
```

## 核心流程

### 智能问答（RAGService）

```
用户提问
  → 混合检索（ChromaDB 向量 + BM25 关键词，各取 Top-K×2）
  → RRF 融合排序（score = Σ 1/(60+rank)），取 Top-K
  → 检索内容注入 system message
  → LLM 生成答案（严格基于文档，不编造）
  → 返回答案 + 来源引用（文件名 + 相似度分数）
```

### 自由闲聊（AgentService + Function Calling）

```
用户消息
  → 第一次调 LLM（携带 TOOL_DEFINITIONS）
  ├── 无 tool_calls → 直接返回答案（闲聊）
  └── 有 tool_calls → 执行对应工具
        ├── get_weather(city)  → 请求 wttr.in → 天气 JSON
        └── web_search(query)  → DuckDuckGo  → 搜索结果
          → 工具结果以 role:tool 消息喂回 LLM
          → 第二次调 LLM → 自然语言最终答案
```

### 扩展新工具（仅需两步）

```python
# 1. 新建 app/tools/calculator.py，实现 DEFINITION 和 run()
# 2. 在 app/tools/__init__.py 注册：
TOOL_DEFINITIONS = [..., calculator.DEFINITION]
TOOL_REGISTRY = {..., "calculator": lambda args: calculator.run(**args)}
```

## 快速开始

### 后端

```bash
cd backend
pip install -r requirements.txt

# 配置 API Key
copy .env.example .env
# 编辑 .env，填入 ZHIPU_API_KEY

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 文档：http://localhost:8000/docs

### 前端

```bash
cd frontend
npm install
npm run dev
```

前端地址：http://localhost:5173

## API 接口

### 知识库与问答

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/upload` | 上传文档（PDF/Word/PPT/TXT，最大 10MB） |
| GET | `/api/documents` | 获取文档列表 |
| DELETE | `/api/documents/{id}` | 删除文档 |
| POST | `/api/query` | 知识库问答（纯 RAG） |
| POST | `/api/chat` | 自由闲聊（Function Calling + 工具） |
| GET | `/api/health` | 健康检查 |

### 会话管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/conversations` | 创建会话 |
| GET | `/api/conversations` | 获取会话列表 |
| PUT | `/api/conversations/{id}` | 更新标题 |
| DELETE | `/api/conversations/{id}` | 删除会话（软删除） |
| GET | `/api/conversations/{id}/messages` | 获取历史消息 |
| POST | `/api/conversations/{id}/query` | 在会话中提问（带上下文） |

## 环境变量

```bash
# 智谱 AI（必填）
ZHIPU_API_KEY=your_api_key
LLM_MODEL=glm-4-air
EMBEDDING_MODEL=embedding-3

# RAG 参数
CHUNK_SIZE=800        # 文本块大小（字符数）
CHUNK_OVERLAP=200     # 块重叠大小
TOP_K=3               # 检索返回数量
TEMPERATURE=0.7       # LLM 生成温度

# 存储路径
CHROMA_PERSIST_DIR=./data/chroma_db
UPLOAD_DIR=./data/uploads
```

获取 API Key：[智谱 AI 开放平台](https://open.bigmodel.cn/) → 控制台 → API Keys
