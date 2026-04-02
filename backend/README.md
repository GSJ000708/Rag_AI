# Backend README

## RAG Knowledge Assistant Backend

基于 FastAPI + 智谱AI + Chroma 的知识库问答系统后端

## 功能特性

✅ 文档上传与解析 (PDF / Word / TXT)  
✅ 自动文本分块与向量化  
✅ 基于 RAG 的智能问答  
✅ 来源文档追溯  
✅ 知识库管理  

## 技术栈

- **框架**: FastAPI 0.109.0
- **LLM**: 智谱 GLM-4-air
- **Embedding**: 智谱 Embedding-3
- **向量数据库**: ChromaDB 0.4.22
- **文档解析**: PyPDF2, python-docx

## 安装与运行

### 1. 激活虚拟环境

```bash
# 如果还没激活，先激活虚拟环境
agent_rag\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
copy .env.example .env

# 编辑 .env 文件，填入你的智谱 API Key
# ZHIPU_API_KEY=your_api_key_here
```

### 4. 启动服务

```bash
# 开发模式（自动重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或者直接运行
python -m app.main
```

### 5. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 接口

### 1. 上传文档
```http
POST /api/upload
Content-Type: multipart/form-data

Body: file (PDF/Word/TXT, max 10MB)

Response:
{
  "document_id": "uuid",
  "filename": "example.pdf",
  "file_size": 1024000,
  "chunks_count": 15,
  "message": "文档上传并处理成功"
}
```

### 2. 知识库问答
```http
POST /api/query
Content-Type: application/json

{
  "question": "你的问题",
  "top_k": 3
}

Response:
{
  "answer": "答案内容...",
  "sources": [
    {
      "content": "相关文档片段...",
      "filename": "example.pdf",
      "page": 1,
      "score": 0.85
    }
  ],
  "question": "你的问题"
}
```

### 3. 查看文档列表
```http
GET /api/documents

Response:
{
  "documents": [
    {
      "document_id": "uuid",
      "filename": "example.pdf",
      "file_size": 1024000,
      "upload_time": "2024-01-01T12:00:00",
      "chunks_count": 15
    }
  ],
  "total": 1
}
```

### 4. 删除文档
```http
DELETE /api/documents/{document_id}

Response:
{
  "message": "文档删除成功",
  "document_id": "uuid"
}
```

### 5. 健康检查
```http
GET /api/health

Response:
{
  "status": "healthy",
  "version": "1.0.0",
  "vectordb_status": "connected",
  "documents_count": 10
}
```

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置管理
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py        # API 路由
│   ├── core/
│   │   ├── __init__.py
│   │   ├── embeddings.py    # Embedding 封装
│   │   ├── llm.py           # LLM 封装
│   │   └── rag.py           # RAG 核心逻辑
│   ├── services/
│   │   ├── __init__.py
│   │   ├── document.py      # 文档处理服务
│   │   └── vectordb.py      # 向量数据库服务
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic 模型
│   └── utils/
│       ├── __init__.py
│       └── file_parser.py   # 文件解析工具
├── data/
│   ├── uploads/             # 上传的文件
│   └── chroma_db/           # Chroma 持久化目录
├── tests/                   # 测试
├── requirements.txt         # Python 依赖
├── .env.example            # 环境变量模板
└── README.md               # 本文档
```

## 配置说明

`.env` 文件中的主要配置：

```bash
# 智谱 API Key (必填)
ZHIPU_API_KEY=your_api_key

# 服务配置
API_HOST=0.0.0.0
API_PORT=8000

# RAG 参数
CHUNK_SIZE=800              # 文本块大小
CHUNK_OVERLAP=200           # 块重叠大小
TOP_K=3                     # 检索文档数量
TEMPERATURE=0.7             # 生成温度

# 模型配置
LLM_MODEL=glm-4-air
EMBEDDING_MODEL=embedding-3
```

## RAG 工作流程

```
用户问题
  ↓
Embedding (问题向量化)
  ↓
向量检索 (Top-K 相似文档)
  ↓
构建 Prompt (问题 + 上下文)
  ↓
LLM 生成答案
  ↓
返回答案 + 来源引用
```

## 获取智谱 API Key

1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册/登录账号
3. 进入控制台 → API Keys
4. 创建新的 API Key
5. 复制到 `.env` 文件

## 参数调优建议

### CHUNK_SIZE (文本块大小)
- **小值 (300-500)**: 更精确，但可能丢失上下文
- **中值 (600-800)**: 平衡，推荐
- **大值 (1000-1500)**: 更多上下文，但可能有噪音

### CHUNK_OVERLAP (块重叠)
- 建议为 CHUNK_SIZE 的 20-25%
- 避免语义在分块边界处断裂

### TOP_K (检索数量)
- **1-2**: 快速响应，适合精确匹配
- **3-5**: 平衡，推荐
- **6-10**: 更全面，但可能引入噪音

### TEMPERATURE (生成温度)
- **0.0-0.3**: 更确定性，适合事实问答
- **0.4-0.7**: 平衡，推荐
- **0.8-1.0**: 更有创造性

## 常见问题

**Q: 安装依赖时出现错误？**  
A: 确保 Python >= 3.9，升级 pip: `python -m pip install --upgrade pip`

**Q: 智谱 API 调用失败？**  
A: 检查 API Key 是否正确，账户是否有余额

**Q: ChromaDB 初始化失败？**  
A: 检查 `data/chroma_db` 目录是否有写权限

**Q: 文档上传后检索不到？**  
A: 检查后端日志，确认文档是否成功向量化

**Q: 答案质量不好？**  
A: 调整 CHUNK_SIZE、TOP_K、TEMPERATURE 等参数

## 开发指南

### 添加新的文档类型

编辑 `app/utils/file_parser.py`:

```python
@staticmethod
def parse_xxx(file_path: str) -> str:
    # 实现解析逻辑
    pass
```

### 自定义 Prompt

编辑 `app/core/rag.py` 中的 `build_prompt` 方法

### 添加新的 API 接口

在 `app/api/routes.py` 中添加新的路由

## 许可证

MIT License
