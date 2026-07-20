"use client";

import { ChatBubble } from "./ChatBubble";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
  isStreaming?: boolean;
}

interface MessageGroupProps {
  messages: Message[];
}

export function MessageGroup({ messages }: MessageGroupProps) {
  if (messages.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center space-y-4 text-muted-foreground p-8">
        <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mb-4">
          <span className="text-primary text-2xl font-bold">A</span>
        </div>
        <h2 className="text-2xl font-semibold text-foreground">How can I help you today?</h2>
        <p className="max-w-md text-sm">I'm your AI assistant. Ask me anything, or pick a suggestion below to get started.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col space-y-6 pb-4">
      {messages.map((message) => (
        <ChatBubble
          key={message.id}
          role={message.role}
          content={message.content}
          timestamp={message.timestamp}
          isStreaming={message.isStreaming}
        />
      ))}
    </div>
  );
}
