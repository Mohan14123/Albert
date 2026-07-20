import { apiClient, createSSEStream } from "@/lib/api-client";

export interface MessageResponse {
  id: string;
  chat_id: string;
  role: "user" | "assistant";
  content: string;
  status: string;
  token_count: number | null;
  created_at: string;
}

export interface MessageListResponse {
  items: MessageResponse[];
  total: number;
  page: number;
  limit: number;
}

export interface SendMessageResponse {
  data: {
    message_id: string;
    status: string;
    content: string;
  };
}

export const messagesApi = {
  list: (chatId: string, page = 1, limit = 50) =>
    apiClient<MessageListResponse>(
      `/chats/${chatId}/messages?page=${page}&limit=${limit}`
    ),

  send: (chatId: string, content: string) =>
    apiClient<SendMessageResponse>(`/chats/${chatId}/messages`, {
      method: "POST",
      body: JSON.stringify({ content }),
    }),

  /**
   * Subscribe to the SSE stream for real-time AI response tokens.
   * Returns a cleanup function to close the connection.
   */
  streamResponse: (
    chatId: string,
    onToken: (token: string) => void,
    onDone: () => void,
    onError?: (error: Error) => void
  ): (() => void) => {
    return createSSEStream(
      `/chats/${chatId}/messages/stream`,
      (event) => {
        if (event.type === "message") {
          const data = event.data as Record<string, unknown>;
          if (data.done) {
            onDone();
          } else if (typeof data.token === "string") {
            onToken(data.token);
          } else if (typeof data.content === "string") {
            onToken(data.content);
          }
        }
      },
      onError,
      onDone
    );
  },
};
