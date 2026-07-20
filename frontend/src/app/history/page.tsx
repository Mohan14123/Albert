"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { AppLayout } from "@/components/layout/AppLayout";
import { ConversationCard } from "@/components/history/ConversationCard";
import { Search } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { chatsApi, Chat } from "@/services/api/chats";

export default function HistoryPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["chatHistory"],
    queryFn: () => chatsApi.list(1, 100),
  });

  const deleteMutation = useMutation({
    mutationFn: (chatId: string) => chatsApi.delete(chatId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["chatHistory"] });
    },
  });

  const renameMutation = useMutation({
    mutationFn: ({ chatId, title }: { chatId: string; title: string }) =>
      chatsApi.rename(chatId, title),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["chatHistory"] });
    },
  });

  const chats = data?.items || [];

  // Filter chats by search query
  const filtered = searchQuery
    ? chats.filter((c) =>
        c.title.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : chats;

  const handleSelect = (chat: Chat) => {
    router.push(`/chat?id=${chat.id}`);
  };

  const handleDelete = (chatId: string) => {
    deleteMutation.mutate(chatId);
  };

  const handleRename = (chatId: string, newTitle: string) => {
    renameMutation.mutate({ chatId, title: newTitle });
  };

  return (
    <AppLayout>
      <div className="flex flex-col h-full bg-background rounded-tl-2xl border-l border-t border-border shadow-soft relative overflow-hidden">
        <header className="h-14 flex items-center justify-between px-6 border-b border-border/40 shrink-0 bg-background/80 backdrop-blur-md z-10 sticky top-0">
          <h1 className="font-semibold text-[15px] tracking-tight">
            Chat History
          </h1>
        </header>

        <div className="p-6 border-b border-border/40 shrink-0">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search conversations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-input/50 border border-border rounded-lg pl-9 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
            />
          </div>
        </div>

        <ScrollArea className="flex-1 px-6">
          <div className="max-w-4xl py-6 space-y-10 min-h-full pb-20">
            {isLoading ? (
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div
                    key={i}
                    className="h-32 bg-secondary/50 animate-pulse rounded-xl"
                  />
                ))}
              </div>
            ) : filtered.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
                <p className="text-lg font-medium">No conversations found</p>
                <p className="text-sm mt-1">
                  {searchQuery
                    ? "Try a different search term"
                    : "Start a new chat to see it here"}
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filtered.map((chat) => (
                  <ConversationCard
                    key={chat.id}
                    conversation={{
                      id: chat.id,
                      title: chat.title,
                      preview: "",
                      updatedAt: chat.updated_at,
                      tags: [],
                      isPinned: false,
                    }}
                    onSelect={() => handleSelect(chat)}
                    onDelete={() => handleDelete(chat.id)}
                    onRename={(newTitle) => handleRename(chat.id, newTitle)}
                  />
                ))}
              </div>
            )}
          </div>
        </ScrollArea>
      </div>
    </AppLayout>
  );
}
