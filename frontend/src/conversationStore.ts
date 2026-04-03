/**
 * 会话状态管理 (Zustand Store)
 */
import { create } from 'zustand';
import { api } from './services/api';
import type { 
  ConversationResponse, 
  MessageResponse
} from './types/api';
import { message as antdMessage } from 'antd';

interface ConversationStore {
  // 状态
  conversations: ConversationResponse[];
  currentConversationId: string | null;
  messages: MessageResponse[];
  loading: boolean;
  sending: boolean;

  // Actions
  loadConversations: () => Promise<void>;
  createConversation: (title?: string) => Promise<ConversationResponse>;
  switchConversation: (conversationId: string) => Promise<void>;
  deleteConversation: (conversationId: string) => Promise<void>;
  updateConversationTitle: (conversationId: string, title: string) => Promise<void>;
  sendMessage: (question: string, top_k?: number) => Promise<void>;
  reset: () => void;
}

export const useConversationStore = create<ConversationStore>((set, get) => ({
  conversations: [],
  currentConversationId: null,
  messages: [],
  loading: false,
  sending: false,

  loadConversations: async () => {
    try {
      set({ loading: true });
      const response = await api.getConversations();
      set({ conversations: response.conversations });
    } catch (error) {
      console.error('Failed to load conversations:', error);
      antdMessage.error('加载会话列表失败');
    } finally {
      set({ loading: false });
    }
  },

  createConversation: async (title?: string) => {
    try {
      const conversation = await api.createConversation({ title });
      set((state) => ({
        conversations: [conversation, ...state.conversations],
        currentConversationId: conversation.id,
        messages: []
      }));
      return conversation;
    } catch (error) {
      console.error('Failed to create conversation:', error);
      antdMessage.error('创建会话失败');
      throw error;
    }
  },

  switchConversation: async (conversationId: string) => {
    try {
      set({ loading: true, currentConversationId: conversationId });
      const messages = await api.getMessages(conversationId);
      set({ messages });
    } catch (error) {
      console.error('Failed to switch conversation:', error);
      antdMessage.error('切换会话失败');
    } finally {
      set({ loading: false });
    }
  },

  deleteConversation: async (conversationId: string) => {
    try {
      await api.deleteConversation(conversationId);
      set((state) => ({
        conversations: state.conversations.filter(c => c.id !== conversationId)
      }));
      const { currentConversationId } = get();
      if (currentConversationId === conversationId) {
        set({ currentConversationId: null, messages: [] });
      }
      antdMessage.success('会话已删除');
    } catch (error) {
      console.error('Failed to delete conversation:', error);
      antdMessage.error('删除会话失败');
    }
  },

  updateConversationTitle: async (conversationId: string, title: string) => {
    try {
      const updated = await api.updateConversation(conversationId, { title });
      set((state) => ({
        conversations: state.conversations.map(c =>
          c.id === conversationId ? { ...c, title: updated.title } : c
        )
      }));
      antdMessage.success('会话标题已更新');
    } catch (error) {
      console.error('Failed to update conversation title:', error);
      antdMessage.error('更新标题失败');
    }
  },

  sendMessage: async (question: string, top_k: number = 3) => {
    const { currentConversationId, messages } = get();
    if (!currentConversationId) {
      antdMessage.error('请先创建或选择一个会话');
      return;
    }

    const wasEmpty = messages.length === 0;

    try {
      set({ sending: true });
      const userMessage: MessageResponse = {
        id: `temp-${Date.now()}`,
        conversation_id: currentConversationId,
        role: 'user',
        content: question,
        created_at: new Date().toISOString()
      };

      set((state) => ({
        messages: [...state.messages, userMessage]
      }));

      const response = await api.queryInConversation(currentConversationId, {
        question,
        top_k
      });

      const assistantMessage: MessageResponse = {
        id: response.message_id,
        conversation_id: currentConversationId,
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
        created_at: new Date().toISOString()
      };

      set((state) => ({
        messages: [...state.messages, assistantMessage]
      }));

      get().loadConversations();
    } catch (error) {
      console.error('Failed to send message:', error);
      antdMessage.error('发送消息失败，请重试');
      set((state) => ({
        messages: state.messages.filter(m => !m.id.startsWith('temp-'))
      }));

      // 如果会话原本为空（刚创建），发送失败后清理空会话
      if (wasEmpty) {
        try {
          await api.deleteConversation(currentConversationId);
          set((state) => ({
            conversations: state.conversations.filter(c => c.id !== currentConversationId),
            currentConversationId: null
          }));
        } catch {
          // 忽略清理失败，不影响主流程
        }
      }
    } finally {
      set({ sending: false });
    }
  },

  reset: () => {
    set({
      conversations: [],
      currentConversationId: null,
      messages: [],
      loading: false,
      sending: false
    });
  }
}));
