import { useState, useRef, useEffect } from 'react';
import { Input, Button, Space, Spin, message } from 'antd';
import { SendOutlined, RobotOutlined, UserOutlined, WechatOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import { api } from '../services/api';
import './ChatPage.css';

const { TextArea } = Input;

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

const FreeChatPage = () => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) {
      message.warning('请输入内容');
      return;
    }

    const userMsg = input.trim();
    setInput('');

    const newMessages: ChatMessage[] = [...messages, { role: 'user', content: userMsg }];
    setMessages(newMessages);
    setSending(true);

    try {
      const history = newMessages.slice(-10).slice(0, -1).map(m => ({
        role: m.role,
        content: m.content,
      }));

      const res = await api.chat({ message: userMsg, history });
      setMessages([...newMessages, { role: 'assistant', content: res.answer }]);
    } catch {
      message.error('请求失败，请重试');
      setMessages(newMessages); // 回滚
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{ display: 'flex', height: 'calc(100vh - 180px)', flexDirection: 'column' }}>
      {/* 标题 */}
      <div style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
        <WechatOutlined style={{ fontSize: 22, color: '#667eea' }} />
        <span style={{ fontSize: 18, fontWeight: 600, color: '#333' }}>自由闲聊</span>
        <span style={{ fontSize: 13, color: '#999', marginLeft: 4 }}>不查知识库，直接与 AI 对话</span>
      </div>

      {/* 消息区域 */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '12px 0',
          display: 'flex',
          flexDirection: 'column',
          gap: 16,
        }}
      >
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', color: '#bbb', marginTop: 60, fontSize: 15 }}>
            <WechatOutlined style={{ fontSize: 48, marginBottom: 12, display: 'block' }} />
            随便聊点什么吧~
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              display: 'flex',
              justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
              gap: 10,
              alignItems: 'flex-start',
            }}
          >
            {msg.role === 'assistant' && (
              <div
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #667eea, #764ba2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                }}
              >
                <RobotOutlined style={{ color: '#fff', fontSize: 16 }} />
              </div>
            )}

            <div
              style={{
                maxWidth: '70%',
                padding: '10px 16px',
                borderRadius: msg.role === 'user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
                background: msg.role === 'user'
                  ? 'linear-gradient(135deg, #667eea, #764ba2)'
                  : '#f5f5f5',
                color: msg.role === 'user' ? '#fff' : '#333',
                fontSize: 14,
                lineHeight: 1.6,
              }}
            >
              {msg.role === 'assistant' ? (
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              ) : (
                msg.content
              )}
            </div>

            {msg.role === 'user' && (
              <div
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: '50%',
                  background: '#e8e8e8',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                }}
              >
                <UserOutlined style={{ color: '#666', fontSize: 16 }} />
              </div>
            )}
          </div>
        ))}

        {sending && (
          <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
            <div
              style={{
                width: 36,
                height: 36,
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #667eea, #764ba2)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <RobotOutlined style={{ color: '#fff', fontSize: 16 }} />
            </div>
            <Spin size="small" />
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 输入区域 */}
      <div style={{ borderTop: '1px solid #f0f0f0', paddingTop: 16 }}>
        <Space.Compact style={{ width: '100%' }}>
          <TextArea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="随便聊点什么... (Enter 发送，Shift+Enter 换行)"
            autoSize={{ minRows: 1, maxRows: 4 }}
            style={{ borderRadius: '8px 0 0 8px', resize: 'none' }}
            disabled={sending}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSend}
            loading={sending}
            style={{
              height: 'auto',
              borderRadius: '0 8px 8px 0',
              background: 'linear-gradient(135deg, #667eea, #764ba2)',
              border: 'none',
            }}
          >
            发送
          </Button>
        </Space.Compact>
      </div>
    </div>
  );
};

export default FreeChatPage;
