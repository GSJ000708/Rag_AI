/**
 * 会话侧边栏组件
 */
import React, { useState } from 'react';
import { List, Button, Input, Modal, Popconfirm, Empty, Spin, Typography } from 'antd';
import {
  PlusOutlined,
  MessageOutlined,
  DeleteOutlined,
  EditOutlined,
  CheckOutlined,
  CloseOutlined
} from '@ant-design/icons';
import type { ConversationResponse } from '../types/api';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import 'dayjs/locale/zh-cn';

dayjs.extend(relativeTime);
dayjs.locale('zh-cn');

const { Text } = Typography;

interface ConversationSidebarProps {
  conversations: ConversationResponse[];
  currentConversationId: string | null;
  loading: boolean;
  onCreateConversation: () => void;
  onSwitchConversation: (id: string) => void;
  onDeleteConversation: (id: string) => void;
  onUpdateTitle: (id: string, title: string) => void;
}

export const ConversationSidebar: React.FC<ConversationSidebarProps> = ({
  conversations,
  currentConversationId,
  loading,
  onCreateConversation,
  onSwitchConversation,
  onDeleteConversation,
  onUpdateTitle
}) => {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState('');

  const handleStartEdit = (conversation: ConversationResponse) => {
    setEditingId(conversation.id);
    setEditingTitle(conversation.title);
  };

  const handleSaveEdit = () => {
    if (editingId && editingTitle.trim()) {
      onUpdateTitle(editingId, editingTitle.trim());
      setEditingId(null);
      setEditingTitle('');
    }
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditingTitle('');
  };

  return (
    <div style={{
      width: '280px',
      height: '100%',
      borderRight: '1px solid #f0f0f0',
      display: 'flex',
      flexDirection: 'column',
      background: '#fafafa'
    }}>
      {/* 顶部：新建会话按钮 */}
      <div style={{ padding: '16px', borderBottom: '1px solid #f0f0f0' }}>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={onCreateConversation}
          block
          size="large"
        >
          新建对话
        </Button>
      </div>

      {/* 会话列表 */}
      <div style={{ flex: 1, overflow: 'auto' }}>
        {loading && conversations.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center' }}>
            <Spin tip="加载中..." />
          </div>
        ) : conversations.length === 0 ? (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="暂无对话"
            style={{ marginTop: '60px' }}
          />
        ) : (
          <List
            dataSource={conversations}
            renderItem={(conversation) => {
              const isActive = conversation.id === currentConversationId;
              const isEditing = editingId === conversation.id;

              return (
                <div
                  key={conversation.id}
                  style={{
                    padding: '12px 16px',
                    cursor: 'pointer',
                    background: isActive ? '#e6f7ff' : 'transparent',
                    borderLeft: isActive ? '3px solid #1890ff' : '3px solid transparent',
                    transition: 'all 0.2s',
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.background = '#f5f5f5';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.background = 'transparent';
                    }
                  }}
                  onClick={() => !isEditing && onSwitchConversation(conversation.id)}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <MessageOutlined style={{ fontSize: '16px', color: '#1890ff' }} />
                    
                    {isEditing ? (
                      <Input
                        value={editingTitle}
                        onChange={(e) => setEditingTitle(e.target.value)}
                        onPressEnter={handleSaveEdit}
                        autoFocus
                        size="small"
                        style={{ flex: 1 }}
                        onClick={(e) => e.stopPropagation()}
                      />
                    ) : (
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <Text
                          strong={isActive}
                          style={{
                            display: 'block',
                            fontSize: '14px',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap'
                          }}
                        >
                          {conversation.title}
                        </Text>
                        {conversation.last_message_preview && (
                          <Text
                            type="secondary"
                            style={{
                              display: 'block',
                              fontSize: '12px',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                              marginTop: '4px'
                            }}
                          >
                            {conversation.last_message_preview}
                          </Text>
                        )}
                      </div>
                    )}

                    {isEditing ? (
                      <div style={{ display: 'flex', gap: '4px' }} onClick={(e) => e.stopPropagation()}>
                        <Button
                          type="text"
                          size="small"
                          icon={<CheckOutlined />}
                          onClick={handleSaveEdit}
                        />
                        <Button
                          type="text"
                          size="small"
                          icon={<CloseOutlined />}
                          onClick={handleCancelEdit}
                        />
                      </div>
                    ) : (
                      <div
                        style={{ display: 'flex', gap: '4px', opacity: isActive ? 1 : 0 }}
                        className="conversation-actions"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <Button
                          type="text"
                          size="small"
                          icon={<EditOutlined />}
                          onClick={() => handleStartEdit(conversation)}
                        />
                        <Popconfirm
                          title="确定要删除这个对话吗？"
                          description="删除后无法恢复"
                          onConfirm={() => onDeleteConversation(conversation.id)}
                          okText="删除"
                          cancelText="取消"
                          okButtonProps={{ danger: true }}
                        >
                          <Button
                            type="text"
                            size="small"
                            icon={<DeleteOutlined />}
                            danger
                          />
                        </Popconfirm>
                      </div>
                    )}
                  </div>

                  <div style={{ marginTop: '4px', fontSize: '12px', color: '#999' }}>
                    {dayjs(conversation.updated_at).fromNow()} · {conversation.message_count} 条消息
                  </div>
                </div>
              );
            }}
          />
        )}
      </div>

      <style>{`
        .conversation-actions {
          transition: opacity 0.2s;
        }
        div:hover .conversation-actions {
          opacity: 1 !important;
        }
      `}</style>
    </div>
  );
};
