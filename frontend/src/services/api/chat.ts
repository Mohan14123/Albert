export interface Conversation {
  id: string;
  title: string;
  preview: string;
  updatedAt: string;
  tags: string[];
  isPinned?: boolean;
}

export interface ChatService {
  getHistory(): Promise<Conversation[]>;
}
