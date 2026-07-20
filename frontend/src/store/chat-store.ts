import { create } from "zustand";
import { chatsApi, Chat } from "@/services/api/chats";
import {
  messagesApi,
  MessageResponse,
} from "@/services/api/messages";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  isStreaming?: boolean;
}

interface ChatState {
  chats: Chat[];
  activeChat: Chat | null;
  messages: ChatMessage[];
  isLoadingChats: boolean;
  isLoadingMessages: boolean;
  isStreaming: boolean;
  streamCleanup: (() => void) | null;

  loadChats: () => Promise<void>;
  createChat: (title?: string) => Promise<Chat>;
  selectChat: (chatId: string) => Promise<void>;
  renameChat: (chatId: string, title: string) => Promise<void>;
  deleteChat: (chatId: string) => Promise<void>;
  sendMessage: (content: string) => Promise<void>;
  clearActiveChat: () => void;
}

function formatTime(dateStr: string): string {
  return new Date(dateStr).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function toUIMessage(msg: MessageResponse): ChatMessage {
  return {
    id: msg.id,
    role: msg.role,
    content: msg.content,
    timestamp: formatTime(msg.created_at),
  };
}

export const useChatStore = create<ChatState>((set, get) => ({
  chats: [],
  activeChat: null,
  messages: [],
  isLoadingChats: false,
  isLoadingMessages: false,
  isStreaming: false,
  streamCleanup: null,

  loadChats: async () => {
    set({ isLoadingChats: true });
    try {
      const res = await chatsApi.list(1, 50);
      set({ chats: res.items });
    } catch (err) {
      console.error("Failed to load chats:", err);
    } finally {
      set({ isLoadingChats: false });
    }
  },

  createChat: async (title?: string) => {
    const chat = await chatsApi.create(title || "New Conversation");
    set((state) => ({ chats: [chat, ...state.chats], activeChat: chat, messages: [] }));
    return chat;
  },

  selectChat: async (chatId: string) => {
    // Cancel any active stream
    const cleanup = get().streamCleanup;
    if (cleanup) cleanup();

    set({ isLoadingMessages: true, isStreaming: false, streamCleanup: null });
    try {
      const [chat, msgRes] = await Promise.all([
        chatsApi.get(chatId),
        messagesApi.list(chatId, 1, 100),
      ]);
      set({
        activeChat: chat,
        messages: msgRes.items.map(toUIMessage),
      });
    } catch (err) {
      console.error("Failed to select chat:", err);
    } finally {
      set({ isLoadingMessages: false });
    }
  },

  renameChat: async (chatId, title) => {
    const updated = await chatsApi.rename(chatId, title);
    set((state) => ({
      chats: state.chats.map((c) => (c.id === chatId ? updated : c)),
      activeChat: state.activeChat?.id === chatId ? updated : state.activeChat,
    }));
  },

  deleteChat: async (chatId) => {
    await chatsApi.delete(chatId);
    set((state) => {
      const newChats = state.chats.filter((c) => c.id !== chatId);
      return {
        chats: newChats,
        activeChat: state.activeChat?.id === chatId ? null : state.activeChat,
        messages: state.activeChat?.id === chatId ? [] : state.messages,
      };
    });
  },

  sendMessage: async (content: string) => {
    const { activeChat } = get();
    if (!activeChat) return;

    // Add user message optimistically
    const userMsg: ChatMessage = {
      id: `temp-${Date.now()}`,
      role: "user",
      content,
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };
    set((state) => ({ messages: [...state.messages, userMsg] }));

    try {
      // Send message to backend
      await messagesApi.send(activeChat.id, content);

      // Add a placeholder assistant message for streaming
      const assistantMsgId = `stream-${Date.now()}`;
      const assistantMsg: ChatMessage = {
        id: assistantMsgId,
        role: "assistant",
        content: "",
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
        isStreaming: true,
      };
      set((state) => ({
        messages: [...state.messages, assistantMsg],
        isStreaming: true,
      }));

      // Open SSE stream to receive AI response tokens
      const cleanup = messagesApi.streamResponse(
        activeChat.id,
        // onToken
        (token: string) => {
          set((state) => ({
            messages: state.messages.map((m) =>
              m.id === assistantMsgId
                ? { ...m, content: m.content + token }
                : m
            ),
          }));
        },
        // onDone
        () => {
          set((state) => ({
            isStreaming: false,
            streamCleanup: null,
            messages: state.messages.map((m) =>
              m.id === assistantMsgId ? { ...m, isStreaming: false } : m
            ),
          }));
        },
        // onError
        (error: Error) => {
          console.error("Stream error:", error);
          set((state) => ({
            isStreaming: false,
            streamCleanup: null,
            messages: state.messages.map((m) =>
              m.id === assistantMsgId
                ? {
                    ...m,
                    isStreaming: false,
                    content:
                      m.content || "Sorry, something went wrong. Please try again.",
                  }
                : m
            ),
          }));
        }
      );

      set({ streamCleanup: cleanup });
    } catch (err) {
      console.error("Failed to send message:", err);
      set({ isStreaming: false });
    }
  },

  clearActiveChat: () => {
    const cleanup = get().streamCleanup;
    if (cleanup) cleanup();
    set({ activeChat: null, messages: [], isStreaming: false, streamCleanup: null });
  },
}));
