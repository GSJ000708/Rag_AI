# RAG Knowledge Assistant

企业级知识库问答系统，基于 RAG (Retrieval-Augmented Generation) 架构

## 功能特性

✅ 文档上传 (PDF / Word / TXT)  
✅ 自动向量化存储  
✅ 智能问答  
✅ 来源追溯  
✅ 知识库管理  

## 技术栈

### 后端
- **框架**: FastAPI
- **LLM**: 智谱 GLM-4-air  
- **Embedding**: 智谱 Embedding-3
- **向量数据库**: Chroma
- **文档解析**: PyPDF2, python-docx

### 前端
- **框架**: React + TypeScript
- **构建工具**: Vite
- **UI**: Ant Design / Material-UI

## 快速开始

### 方式1: 使用批处理脚本 (推荐)

```bash
setup.bat
```

### 方式2: 手动设置

#### 1. 创建项目结构

```bash
python setup_project.py
```

#### 2. 创建虚拟环境

```bash
cd backend
python -m venv venv
```

#### 3. 激活虚拟环境

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

#### 4. 安装依赖

```bash
pip install -r requirements.txt
```

#### 5. 配置环境变量

复制 `.env.example` 为 `.env` 并填入智谱 API Key:

```bash
copy .env.example .env
```

编辑 `.env` 文件，设置你的 API Key:
```
ZHIPU_API_KEY=your_api_key_here
```

#### 6. 启动后端服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 API 文档: http://localhost:8000/docs

## 项目结构

```
ai_agent_rag/
├── backend/               # 后端服务
│   ├── app/
│   │   ├── api/          # API 路由
│   │   ├── core/         # RAG 核心逻辑
│   │   ├── services/     # 服务层
│   │   ├── models/       # 数据模型
│   │   ├── utils/        # 工具函数
│   │   ├── config.py     # 配置管理
│   │   └── main.py       # 应用入口
│   ├── data/             # 数据存储
│   │   ├── uploads/      # 上传的文档
│   │   └── chroma_db/    # 向量数据库
│   ├── tests/            # 测试
│   ├── requirements.txt  # Python 依赖
│   ├── .env.example      # 环境变量示例
│   └── README.md         # 后端文档
├── frontend/             # 前端应用 (待创建)
├── setup_project.py      # 项目初始化脚本
├── setup.bat             # Windows 快速安装脚本
└── README.md             # 项目文档
```

## RAG 工作流程

```
1. 文档上传 
   ↓
2. 文本提取 & 分块 (Chunk Size: 800, Overlap: 200)
   ↓
3. 向量化 (智谱 Embedding-3)
   ↓
4. 存储到 Chroma
   ↓
5. 用户提问
   ↓
6. 问题向量化
   ↓
7. 相似度检索 (Top-K: 3)
   ↓
8. 构建 Prompt (问题 + 上下文)
   ↓
9. LLM 生成答案 (智谱 GLM-4-air)
   ↓
10. 返回答案 + 来源引用
```

## API 接口

### 上传文档
```
POST /api/upload
Content-Type: multipart/form-data

Body: file (PDF/Word/TXT, max 10MB)
```

### 问答
```
POST /api/query
Content-Type: application/json

{
  "question": "你的问题"
}
```

### 查看文档列表
```
GET /api/documents
```

### 删除文档
```
DELETE /api/documents/{document_id}
```

### 健康检查
```
GET /api/health
```

## 配置说明

主要配置项 (`.env`):

```bash
# 智谱 AI API Key
ZHIPU_API_KEY=your_api_key

# RAG 参数
CHUNK_SIZE=800          # 文本块大小
CHUNK_OVERLAP=200       # 块重叠大小
TOP_K=3                 # 检索文档数量
TEMPERATURE=0.7         # 生成温度

# 模型选择
LLM_MODEL=glm-4-air
EMBEDDING_MODEL=embedding-3
```

## 获取智谱 API Key

1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册/登录账号
3. 进入控制台 → API Keys
4. 创建新的 API Key
5. 复制到 `.env` 文件

## 开发指南

### 添加新的文档类型

在 `backend/app/utils/file_parser.py` 中添加解析器

### 调整 RAG 参数

修改 `backend/.env` 中的配置:
- `CHUNK_SIZE`: 增大可获得更多上下文，减小可提高精确度
- `TOP_K`: 增大可获得更多相关文档，但可能引入噪音
- `TEMPERATURE`: 0-1之间，越低越确定性

### 自定义 Prompt

修改 `backend/app/core/rag.py` 中的 Prompt 模板

## 常见问题

**Q: 安装依赖时出现错误？**  
A: 确保 Python 版本 >= 3.9，升级 pip: `python -m pip install --upgrade pip`

**Q: 智谱 API 调用失败？**  
A: 检查 API Key 是否正确，账户是否有余额

**Q: 文档上传后无法检索到？**  
A: 检查文档是否成功向量化，查看后端日志

**Q: 答案质量不好？**  
A: 尝试调整 `CHUNK_SIZE`、`TOP_K` 等参数

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request!
