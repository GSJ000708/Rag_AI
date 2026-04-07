# RAG Knowledge Assistant

基于 RAG (Retrieval-Augmented Generation) 架构的知识库问答系统。

## 功能特性

- 文档上传 (PDF / Word / TXT)
- 自动向量化存储
- 混合检索（向量语义 + BM25 关键词 + RRF 融合）
- 多轮对话 & 会话管理
- 智能问答 + 来源追溯
- 知识库管理

## 技术栈

### 后端
- **框架**: FastAPI
- **LLM**: 智谱 GLM-4-air
- **Embedding**: 智谱 Embedding-3
- **向量数据库**: ChromaDB（本地持久化）
- **关键词检索**: rank-bm25（BM25Okapi）
- **融合算法**: RRF（Reciprocal Rank Fusion）
- **会话存储**: SQLite（SQLAlchemy ORM）
- **文档解析**: PyPDF2, python-docx, python-pptx

### 前端
- **框架**: React + TypeScript
- **构建工具**: Vite
- **UI**: Ant Design

## 项目结构

```
Rag_AI/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes.py              # 文档上传、问答、知识库管理接口
│   │   │   └── conversation_routes.py # 会话管理接口
│   │   ├── core/
│   │   │   ├── embeddings.py          # 智谱 Embedding 封装
│   │   │   ├── llm.py                 # 智谱 LLM 封装
│   │   │   └── rag.py                 # RAG 核心流程
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
│   │   ├── database.py                # 数据库连接（SQLite）
│   │   └── main.py                    # 应用入口
│   ├── data/
│   │   ├── uploads/                   # 上传的原始文档
│   │   ├── chroma_db/                 # ChromaDB 向量数据
│   │   └── conversations.db           # 会话记录（SQLite）
│   ├── requirements.txt
│   ├── .env                           # 环境变量（本地，不提交）
│   └── .env.example                   # 环境变量示例
├── frontend/
│   ├── src/
│   ├── index.html
│   └── package.json
└── README.md
```

## 快速开始

### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
copy .env.example .env
```

编辑 `.env`，填入智谱 API Key：

```
ZHIPU_API_KEY=your_api_key_here
```

### 3. 启动后端

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 文档：http://localhost:8000/docs

### 4. 启动前端

```bash
cd frontend
npm install
npm run dev
```

## RAG 工作流程

```
文档上传
  ↓
文本提取 & 分块（Chunk Size: 800，Overlap: 200）
  ↓
向量化（智谱 Embedding-3）→ 存入 ChromaDB
  ↓
用户提问
  ↓
并行检索：
  ├── 向量语义检索（ChromaDB cosine 相似度）
  └── 关键词检索（BM25Okapi）
  ↓
RRF 融合排序（Top-K: 3）
  ↓
构建 Prompt（问题 + 检索上下文 + 历史对话）
  ↓
LLM 生成答案（智谱 GLM-4-air）
  ↓
返回答案 + 来源引用，保存至会话记录
```

## API 接口

### 知识库

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/upload` | 上传文档（PDF/Word/TXT，最大 10MB）|
| GET | `/api/documents` | 获取文档列表 |
| DELETE | `/api/documents/{document_id}` | 删除文档 |
| POST | `/api/query` | 问答（支持传入 conversation_id）|
| GET | `/api/health` | 健康检查 |

### 会话管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/conversations` | 创建新会话 |
| GET | `/api/conversations` | 获取会话列表 |
| GET | `/api/conversations/{id}/messages` | 获取会话历史消息 |
| DELETE | `/api/conversations/{id}` | 删除会话 |

## 配置说明

```bash
# 智谱 AI
ZHIPU_API_KEY=your_api_key
LLM_MODEL=glm-4-air
EMBEDDING_MODEL=embedding-3

# RAG 参数
CHUNK_SIZE=800        # 文本块大小
CHUNK_OVERLAP=200     # 块重叠大小
TOP_K=3               # 检索返回数量
TEMPERATURE=0.7       # 生成温度

# 存储路径
CHROMA_PERSIST_DIR=./data/chroma_db
UPLOAD_DIR=./data/uploads
```

## 获取智谱 API Key

1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册/登录 → 控制台 → API Keys → 创建
3. 复制到 `.env` 文件

## 常见问题

**Q: `ModuleNotFoundError: No module named 'app'`**  
A: 需要在 `backend/` 目录下运行 uvicorn，不是项目根目录。

**Q: 安装依赖报错？**  
A: 确保 Python >= 3.9，并升级 pip：`python -m pip install --upgrade pip`

**Q: 智谱 API 调用失败？**  
A: 检查 API Key 是否正确，账户是否有余额。

**Q: 答案质量不好？**  
A: 调整 `CHUNK_SIZE`、`TOP_K` 参数，或优化文档内容。
