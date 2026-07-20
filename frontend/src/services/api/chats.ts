import { apiClient } from "@/lib/api-client";

export interface Chat {
  id: string;
  title: string;
  archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface ChatListResponse {
  items: Chat[];
  total: number;
  page: number;
  limit: number;
}

export const chatsApi = {
  list: (page = 1, limit = 20) =>
    apiClient<ChatListResponse>(`/chats?page=${page}&limit=${limit}`),

  create: (title: string) =>
    apiClient<Chat>("/chats", {
      method: "POST",
      body: JSON.stringify({ title }),
    }),

  get: (chatId: string) => apiClient<Chat>(`/chats/${chatId}`),

  rename: (chatId: string, title: string) =>
    apiClient<Chat>(`/chats/${chatId}`, {
      method: "PATCH",
      body: JSON.stringify({ title }),
    }),

  delete: (chatId: string) =>
    apiClient<void>(`/chats/${chatId}`, {
      method: "DELETE",
    }),
};
