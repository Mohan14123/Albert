import { ChatService, Conversation } from "../api/chat";

const mockConversations: Conversation[] = [
  {
    id: "1",
    title: "React Performance Tips",
    preview: "To optimize React performance, you should use useMemo and useCallback...",
    updatedAt: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    tags: ["React", "Performance"],
    isPinned: true,
  },
  {
    id: "2",
    title: "Explain Quantum Computing",
    preview: "Quantum computing is a rapidly-emerging technology that harnesses the laws of...",
    updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    tags: ["Science", "Physics"],
  },
  {
    id: "3",
    title: "Next.js 14 App Router Setup",
    preview: "The new app router in Next.js 14 introduces React Server Components...",
    updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(),
    tags: ["Next.js", "Web Dev"],
  }
];

export const mockChatService: ChatService = {
  getHistory: async () => {
    // Simulate network delay
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(mockConversations);
      }, 500);
    });
  }
};
