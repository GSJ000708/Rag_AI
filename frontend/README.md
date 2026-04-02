# Frontend - RAG Knowledge Assistant

React + TypeScript + Vite + Ant Design 前端应用

## 功能特性

- ✅ 智能问答对话界面
- ✅ 文档上传（拖拽上传）
- ✅ 知识库管理
- ✅ 实时消息流
- ✅ 来源文档展示
- ✅ 响应式设计

## 技术栈

- React 18
- TypeScript
- Vite
- Ant Design 5
- React Router
- Axios
- React Markdown

## 安装

```bash
npm install
```

## 开发

```bash
npm run dev
```

访问: http://localhost:3000

## 构建

```bash
npm run build
```

## 项目结构

```
src/
├── components/       # 组件
│   └── Layout.tsx   # 布局组件
├── pages/           # 页面
│   ├── ChatPage.tsx        # 问答页面
│   ├── UploadPage.tsx      # 上传页面
│   └── ManagementPage.tsx  # 管理页面
├── services/        # 服务
│   └── api.ts      # API 调用
├── types/           # 类型定义
│   └── api.ts      # API 类型
├── App.tsx          # 根组件
├── main.tsx         # 入口文件
└── index.css        # 全局样式
```

## 配置

### 环境变量

创建 `.env` 文件：

```
VITE_API_BASE_URL=http://localhost:8000
```

### 代理配置

`vite.config.ts` 中已配置代理：

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  }
}
```

## 页面说明

### 智能问答 (`/chat`)
- 对话式问答界面
- 实时消息流
- 显示参考来源
- 支持 Markdown 渲染

### 上传文档 (`/upload`)
- 拖拽上传文件
- 支持 PDF、Word、TXT
- 实时上传进度
- 上传记录展示

### 知识库管理 (`/management`)
- 文档列表展示
- 统计信息（文档数、大小、分块数）
- 删除文档
- 刷新列表

## API 集成

所有 API 调用在 `src/services/api.ts` 中定义：

- `uploadDocument(file)` - 上传文档
- `query(request)` - 问答查询
- `getDocuments()` - 获取文档列表
- `deleteDocument(id)` - 删除文档
- `health()` - 健康检查

## 开发建议

### 添加新页面

1. 在 `src/pages/` 创建新组件
2. 在 `App.tsx` 添加路由
3. 在 `Layout.tsx` 添加菜单项

### 调用 API

```typescript
import { api } from '../services/api';

const response = await api.query({ question: '你好' });
```

### 错误处理

```typescript
try {
  const response = await api.query({ question: '你好' });
} catch (error: any) {
  message.error(error.response?.data?.detail || '请求失败');
}
```

## 许可证

MIT License
