"use client";

import { useState } from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { ChatInput } from "@/components/chat/ChatInput";
import { MessageGroup, Message } from "@/components/chat/MessageGroup";
import { ScrollArea } from "@/components/ui/scroll-area";

const initialMessages: Message[] = [
  {
    id: "1",
    role: "assistant",
    content: "Hello! I'm your AI assistant. How can I help you today?",
    timestamp: '10:00 AM'
  }
];

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [isTyping, setIsTyping] = useState(false);

  const handleSend = (content: string) => {
    const newUserMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    
    setMessages((prev) => [...prev, newUserMessage]);
    setIsTyping(true);

    // Mock AI response
    setTimeout(() => {
      const aiResponseId = (Date.now() + 1).toString();
      setMessages((prev) => [
        ...prev,
        {
          id: aiResponseId,
          role: "assistant",
          content: "This is a beautiful, premium interface. I am processing your request...",
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          isStreaming: true
        }
      ]);

      // Simulate stream end
      setTimeout(() => {
        setMessages((prev) => prev.map(msg => 
          msg.id === aiResponseId ? { ...msg, isStreaming: false, content: "This is a beautiful, premium interface. I've successfully processed your request." } : msg
        ));
        setIsTyping(false);
      }, 1500);

    }, 600);
  };

  return (
    <AppLayout>
      <div className="flex flex-col h-full bg-background rounded-tl-2xl border-l border-t border-border shadow-soft relative overflow-hidden">
        {/* Top Section */}
        <header className="h-14 flex items-center justify-between px-6 border-b border-border/40 shrink-0 bg-background/80 backdrop-blur-md z-10 sticky top-0">
          <div className="flex items-center gap-3">
            <h1 className="font-semibold text-[15px] tracking-tight">New Conversation</h1>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-semibold px-2.5 py-1 bg-primary/10 text-primary rounded-full uppercase tracking-wider">
              GPT-4
            </span>
          </div>
        </header>

        {/* Main Section - Messages */}
        <ScrollArea className="flex-1 px-4 py-6 md:px-8">
          <div className="max-w-3xl mx-auto min-h-full">
            <MessageGroup messages={messages} />
          </div>
        </ScrollArea>

        {/* Bottom Section - Input */}
        <div className="p-4 md:p-6 shrink-0 bg-gradient-to-t from-background via-background to-transparent pt-8">
          <div className="max-w-3xl mx-auto">
            <ChatInput onSend={handleSend} isLoading={isTyping} />
            <div className="text-center mt-3">
              <span className="text-[11px] text-muted-foreground/70 font-medium">
                AI can make mistakes. Consider verifying important information.
              </span>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
