"use client";

import { useEffect, useRef, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { AppLayout } from "@/components/layout/AppLayout";
import { ChatInput } from "@/components/chat/ChatInput";
import { MessageGroup } from "@/components/chat/MessageGroup";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useChatStore } from "@/store/chat-store";

function ChatContent() {
  const searchParams = useSearchParams();
  const chatId = searchParams.get("id");
  const scrollRef = useRef<HTMLDivElement>(null);

  const {
    activeChat,
    messages,
    isStreaming,
    isLoadingMessages,
    selectChat,
    createChat,
    sendMessage,
  } = useChatStore();

  // Load chat on mount — either from URL param or create new
  useEffect(() => {
    if (chatId) {
      selectChat(chatId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chatId]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async (content: string) => {
    if (!activeChat) {
      // Create a new chat first, then send the message
      const chat = await createChat(content.slice(0, 60));
      // Update URL without full navigation
      window.history.replaceState(null, "", `/chat?id=${chat.id}`);
    }
    await sendMessage(content);
  };

  return (
    <div className="flex flex-col h-full bg-background rounded-tl-2xl border-l border-t border-border shadow-soft relative overflow-hidden">
      {/* Top Section */}
      <header className="h-14 flex items-center justify-between px-6 border-b border-border/40 shrink-0 bg-background/80 backdrop-blur-md z-10 sticky top-0">
        <div className="flex items-center gap-3">
          <h1 className="font-semibold text-[15px] tracking-tight">
            {activeChat?.title || "New Conversation"}
          </h1>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-semibold px-2.5 py-1 bg-primary/10 text-primary rounded-full tracking-wider flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            Albert AI Gateway
          </span>
        </div>
      </header>

      {/* Main Section - Messages */}
      <ScrollArea className="flex-1 px-4 py-6 md:px-8" ref={scrollRef}>
        <div className="max-w-3xl mx-auto min-h-full">
          {isLoadingMessages ? (
            <div className="flex flex-col items-center justify-center h-full py-20">
              <div className="w-8 h-8 border-2 border-primary/30 border-t-primary rounded-full animate-spin" />
              <p className="mt-4 text-sm text-muted-foreground">
                Loading messages...
              </p>
            </div>
          ) : (
            <MessageGroup messages={messages} />
          )}
        </div>
      </ScrollArea>

      {/* Bottom Section - Input */}
      <div className="p-4 md:p-6 shrink-0 bg-gradient-to-t from-background via-background to-transparent pt-8">
        <div className="max-w-3xl mx-auto">
          <ChatInput onSend={handleSend} isLoading={isStreaming} />
          <div className="text-center mt-3">
            <span className="text-[11px] text-muted-foreground/70 font-medium">
              AI can make mistakes. Consider verifying important information.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ChatPage() {
  return (
    <AppLayout>
      <Suspense fallback={<div className="flex-1 bg-background rounded-tl-2xl border-l border-t border-border shadow-soft flex items-center justify-center">Loading...</div>}>
        <ChatContent />
      </Suspense>
    </AppLayout>
  );
}
