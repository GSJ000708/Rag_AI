import { useState, useRef, useEffect } from 'react';
import { Input, Button, Card, Space, Tag, Spin, Empty, message } from 'antd';
import { SendOutlined, RobotOutlined, UserOutlined, ThunderboltOutlined } from '@ant-design/icons';
import { useConversationStore } from '../conversationStore';
import { ConversationSidebar } from '../components/ConversationSidebar';
import type { SourceDocument } from '../types/api';
import ReactMarkdown from 'react-markdown';
import './ChatPage.css';

const { TextArea } = Input;

const ChatPage = () => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // 使用 Zustand store
  const {
    conversations,
    currentConversationId,
    messages,
    loading,
    sending,
    loadConversations,
    createConversation,
    switchConversation,
    deleteConversation,
    updateConversationTitle,
    sendMessage
  } = useConversationStore();

  // 初始化：加载会话列表
  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 发送消息
  const handleSend = async () => {
    if (!input.trim()) {
      message.warning('请输入问题');
      return;
    }

    const question = input.trim();
    setInput('');

    // 如果没有当前会话，先创建一个
    if (!currentConversationId) {
      try {
        await createConversation();
      } catch {
        return;
      }
    }

    await sendMessage(question);
  };

  // 创建新会话的处理
  const handleCreateConversation = async () => {
    await createConversation();
  };

  const quickQuestions = [
    '这个文档主要讲了什么？',
    '请总结一下关键要点',
    '有哪些重要的结论？',
  ];

  return (
    <div style={{ height: '100%', display: 'flex' }}>
      {/* 左侧：会话列表侧边栏 */}
      <ConversationSidebar
        conversations={conversations}
        currentConversationId={currentConversationId}
        loading={loading}
        onCreateConversation={handleCreateConversation}
        onSwitchConversation={switchConversation}
        onDeleteConversation={deleteConversation}
        onUpdateTitle={updateConversationTitle}
      />

      {/* 右侧：聊天区域 */}
      <div style={{ flex: 1, height: '100%', display: 'flex', flexDirection: 'column', padding: '24px' }}>
        {/* 标题区域 */}
        <div style={{ marginBottom: '24px' }}>
          <h1 style={{ 
            fontSize: '28px', 
            fontWeight: 'bold',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            marginBottom: '8px',
          }}>
            💬 智能问答
          </h1>
          <p style={{ color: '#666', margin: 0 }}>
            基于 RAG 技术，从知识库中检索相关内容并生成精准答案
          </p>
        </div>

        {/* 消息列表 */}
        <div
          style={{
            flex: 1,
            overflowY: 'auto',
            marginBottom: '20px',
            padding: '20px',
            background: 'linear-gradient(to bottom, #f9fafb, #ffffff)',
            borderRadius: '12px',
            border: '1px solid #e5e7eb',
          }}
        >
          {!currentConversationId ? (
            <div style={{ textAlign: 'center', marginTop: '60px' }}>
              <Empty
                description={
                  <div>
                    <p style={{ fontSize: '16px', color: '#666', marginBottom: '20px' }}>
                      请先创建或选择一个会话开始对话
                    </p>
                    <Button
                      type="primary"
                      size="large"
                      onClick={handleCreateConversation}
                      style={{
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        border: 'none',
                      }}
                    >
                      创建新会话
                    </Button>
                  </div>
                }
              />
            </div>
          ) : messages.length === 0 ? (
            <div style={{ textAlign: 'center', marginTop: '60px' }}>
              <Empty
                description={
                  <div>
                    <p style={{ fontSize: '16px', color: '#666', marginBottom: '20px' }}>
                      还没有对话，试试这些问题开始吧！
                    </p>
                    <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                      {quickQuestions.map((q, idx) => (
                        <Button
                          key={idx}
                          type="dashed"
                          size="large"
                          icon={<ThunderboltOutlined />}
                          onClick={() => setInput(q)}
                          style={{ width: '400px', maxWidth: '100%' }}
                        >
                          {q}
                        </Button>
                      ))}
                    </Space>
                  </div>
                }
              />
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                style={{
                  marginBottom: '24px',
                  display: 'flex',
                  justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  animation: 'fadeInUp 0.3s ease-out',
                }}
              >
                {/* AI 头像在左侧 */}
                {msg.role === 'assistant' && (
                <div style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: '#667eea',
                  color: '#fff',
                  marginRight: '12px',
                  flexShrink: 0,
                }}>
                  <RobotOutlined style={{ fontSize: '20px' }} />
                </div>
              )}
              
              <div style={{ 
                maxWidth: '70%',
                display: 'flex',
                flexDirection: 'column',
              }}>
                {/* 用户名标签 */}
                  <div style={{ 
                    marginBottom: '8px',
                    display: 'flex',
                    justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  }}>
                    <span style={{ 
                      fontSize: '13px',
                      color: '#666',
                      fontWeight: 500,
                    }}>
                      {msg.role === 'user' ? '我' : 'AI 助手'}
                    </span>
                  </div>
                  
                  {/* 消息卡片 */}
                  <Card
                    style={{
                      background: msg.role === 'user' 
                        ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                        : '#fff',
                      color: msg.role === 'user' ? '#fff' : '#000',
                      border: msg.role === 'user' ? 'none' : '1px solid #e5e7eb',
                      boxShadow: msg.role === 'user' 
                        ? '0 4px 12px rgba(102, 126, 234, 0.4)'
                        : '0 2px 8px rgba(0, 0, 0, 0.08)',
                      borderRadius: msg.role === 'user' ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
                    }}
                    bodyStyle={{ padding: '16px' }}
                  >
                    <Space direction="vertical" style={{ width: '100%' }} size="middle">
                      <div 
                        className="chat-message-content"
                        style={{ 
                          lineHeight: '1.6',
                          fontSize: '15px',
                        }}
                      >
                        {msg.role === 'assistant' ? (
                        <ReactMarkdown
                          components={{
                            p: ({ children }) => <p>{children}</p>,
                            ul: ({ children }) => <ul>{children}</ul>,
                            ol: ({ children }) => <ol>{children}</ol>,
                            li: ({ children }) => <li>{children}</li>,
                            h1: ({ children }) => <h1>{children}</h1>,
                            h2: ({ children }) => <h2>{children}</h2>,
                            h3: ({ children }) => <h3>{children}</h3>,
                            code: ({ children, className }) => {
                              const isInline = !className;
                              return isInline ? <code>{children}</code> : <code className={className}>{children}</code>;
                            },
                            pre: ({ children }) => <pre>{children}</pre>,
                          }}
                        >
                          {msg.content}
                        </ReactMarkdown>
                      ) : (
                        <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
                      )}
                    </div>
                    {msg.sources && msg.sources.length > 0 && (
                      <div style={{ marginTop: '12px' }}>
                        <div style={{ 
                          marginBottom: '8px', 
                          fontWeight: 'bold',
                          color: '#667eea',
                          fontSize: '14px',
                        }}>
                          📚 参考来源
                        </div>
                        {msg.sources.map((source, idx) => (
                          <Card
                            key={idx}
                            size="small"
                            style={{ 
                              marginBottom: '8px', 
                              background: 'linear-gradient(to right, #f9fafb, #ffffff)',
                              border: '1px solid #e5e7eb',
                              borderRadius: '8px',
                            }}
                            bodyStyle={{ padding: '12px' }}
                          >
                            <Space direction="vertical" size="small" style={{ width: '100%' }}>
                              <Space wrap>
                                <Tag color="blue" style={{ borderRadius: '4px' }}>
                                  {source.filename}
                                </Tag>
                                <Tag color="green" style={{ borderRadius: '4px' }}>
                                  相似度: {(source.score * 100).toFixed(1)}%
                                </Tag>
                              </Space>
                              <div style={{ 
                                fontSize: '13px', 
                                color: '#666',
                                lineHeight: '1.5',
                              }}>
                                {source.content}
                              </div>
                            </Space>
                          </Card>
                        ))}
                      </div>
                    )}
                  </Space>
                </Card>
                </div>
                
                {/* 用户头像在右侧 */}
                {msg.role === 'user' && (
                <div style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: '#fff',
                  marginLeft: '12px',
                  flexShrink: 0,
                }}>
                  <UserOutlined style={{ fontSize: '20px' }} />
                </div>
              )}
              </div>
            ))
          )}
          {sending && (
            <div style={{ 
              textAlign: 'center', 
              padding: '30px',
              animation: 'fadeInUp 0.3s ease-out',
            }}>
              <Spin size="large" tip={
                <span style={{ color: '#667eea', fontWeight: 500 }}>
                  AI 正在思考中...
                </span>
              } />
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* 输入框 */}
        <div style={{
          background: '#fff',
          padding: '16px',
          borderRadius: '12px',
          border: '1px solid #e5e7eb',
          boxShadow: '0 -2px 8px rgba(0, 0, 0, 0.05)',
        }}>
          <Space.Compact style={{ width: '100%' }}>
            <TextArea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onPressEnter={(e) => {
                if (!e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="输入你的问题... (Shift+Enter 换行，Enter 发送)"
              autoSize={{ minRows: 2, maxRows: 6 }}
              disabled={sending}
              style={{ 
                borderRadius: '8px 0 0 8px',
                fontSize: '15px',
              }}
            />
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={handleSend}
              loading={sending}
              disabled={sending}
              style={{ 
                height: 'auto',
                borderRadius: '0 8px 8px 0',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                border: 'none',
                minWidth: '100px',
                fontSize: '15px',
                fontWeight: 500,
              }}
            >
              发送
            </Button>
          </Space.Compact>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
