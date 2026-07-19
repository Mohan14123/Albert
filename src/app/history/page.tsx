"use client";

import { useQuery } from "@tanstack/react-query";
import { AppLayout } from "@/components/layout/AppLayout";
import { ConversationCard } from "@/components/history/ConversationCard";
import { mockChatService } from "@/services/mocks/chat-mock";
import { Search } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";

export default function HistoryPage() {
  const { data: conversations, isLoading } = useQuery({
    queryKey: ["chatHistory"],
    queryFn: () => mockChatService.getHistory(),
  });

  const pinned = conversations?.filter(c => c.isPinned) || [];
  const recent = conversations?.filter(c => !c.isPinned) || [];

  return (
    <AppLayout>
      <div className="flex flex-col h-full bg-background rounded-tl-2xl border-l border-t border-border shadow-soft relative overflow-hidden">
        <header className="h-14 flex items-center justify-between px-6 border-b border-border/40 shrink-0 bg-background/80 backdrop-blur-md z-10 sticky top-0">
          <h1 className="font-semibold text-[15px] tracking-tight">Chat History</h1>
        </header>

        <div className="p-6 border-b border-border/40 shrink-0">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input 
              type="text" 
              placeholder="Search conversations..." 
              className="w-full bg-input/50 border border-border rounded-lg pl-9 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
            />
          </div>
        </div>

        <ScrollArea className="flex-1 px-6">
          <div className="max-w-4xl py-6 space-y-10 min-h-full pb-20">
            {isLoading ? (
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-32 bg-secondary/50 animate-pulse rounded-xl" />
                ))}
              </div>
            ) : (
              <>
                {pinned.length > 0 && (
                  <section>
                    <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-4 px-1">Pinned</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {pinned.map(conv => (
                        <ConversationCard key={conv.id} conversation={conv} />
                      ))}
                    </div>
                  </section>
                )}

                {recent.length > 0 && (
                  <section>
                    <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-4 px-1">Recent</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {recent.map(conv => (
                        <ConversationCard key={conv.id} conversation={conv} />
                      ))}
                    </div>
                  </section>
                )}
              </>
            )}
          </div>
        </ScrollArea>
      </div>
    </AppLayout>
  );
}
