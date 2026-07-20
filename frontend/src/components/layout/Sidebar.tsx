"use client";

import { useEffect } from "react";
import { useUIStore } from "@/store/ui-store";
import { useChatStore } from "@/store/chat-store";
import { useAuthStore } from "@/store/auth-store";
import {
  MessageSquare,
  Plus,
  PanelLeftClose,
  PanelLeftOpen,
  LogOut,
  History,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useRouter } from "next/navigation";

export function Sidebar() {
  const { isSidebarOpen, toggleSidebar } = useUIStore();
  const { chats, activeChat, loadChats, createChat, selectChat } =
    useChatStore();
  const { logout, user } = useAuthStore();
  const router = useRouter();

  // Load chats on sidebar mount
  useEffect(() => {
    loadChats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleNewChat = async () => {
    await createChat();
    router.push("/chat");
  };

  const handleSelectChat = async (chatId: string) => {
    await selectChat(chatId);
    router.push(`/chat?id=${chatId}`);
  };

  const handleLogout = async () => {
    await logout();
    router.push("/");
  };

  const recentChats = chats.slice(0, 10);

  return (
    <aside
      className={cn(
        "flex flex-col h-full bg-sidebar border-r border-sidebar-border transition-all duration-300",
        isSidebarOpen ? "w-[280px]" : "w-0 opacity-0 overflow-hidden"
      )}
    >
      <div className="p-4 flex items-center justify-between border-b border-sidebar-border">
        <div className="flex items-center gap-2 text-sidebar-foreground">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-primary-foreground font-bold">
            A
          </div>
          <div className="flex flex-col">
            <span className="font-semibold text-sm">Albert AI</span>
            {user && (
              <span className="text-[10px] text-muted-foreground truncate max-w-[180px]">
                {user.email}
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="p-3 space-y-1">
        <button
          onClick={handleNewChat}
          className="w-full flex items-center gap-2 bg-sidebar-accent hover:bg-sidebar-accent/80 text-sidebar-accent-foreground px-3 py-2 rounded-md transition-colors text-sm font-medium"
        >
          <Plus className="w-4 h-4" />
          New Chat
        </button>
        <button
          onClick={() => router.push("/history")}
          className="w-full flex items-center gap-2 px-3 py-2 text-sm rounded-md hover:bg-sidebar-accent text-sidebar-foreground text-left transition-colors"
        >
          <History className="w-4 h-4 text-muted-foreground" />
          Chat History
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-3 py-2 space-y-6">
        <div>
          <h3 className="text-xs font-semibold text-muted-foreground mb-2 px-2 uppercase tracking-wider">
            Recent Chats
          </h3>
          <div className="space-y-1">
            {recentChats.length === 0 ? (
              <p className="text-xs text-muted-foreground px-2 py-4 text-center">
                No conversations yet
              </p>
            ) : (
              recentChats.map((chat) => (
                <button
                  key={chat.id}
                  onClick={() => handleSelectChat(chat.id)}
                  className={cn(
                    "w-full flex items-center gap-2 px-2 py-1.5 text-sm rounded-md hover:bg-sidebar-accent text-sidebar-foreground text-left transition-colors",
                    activeChat?.id === chat.id &&
                      "bg-sidebar-accent text-sidebar-accent-foreground"
                  )}
                >
                  <MessageSquare className="w-4 h-4 text-muted-foreground shrink-0" />
                  <span className="truncate">{chat.title}</span>
                </button>
              ))
            )}
          </div>
        </div>
      </div>

      <div className="p-3 border-t border-sidebar-border">
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-2 px-2 py-1.5 mb-1 text-sm rounded-md hover:bg-destructive/10 text-destructive transition-colors"
        >
          <LogOut className="w-4 h-4" />
          <span>Log out</span>
        </button>
        <button
          onClick={toggleSidebar}
          className="w-full flex items-center gap-2 px-2 py-1.5 text-sm rounded-md hover:bg-sidebar-accent text-sidebar-foreground transition-colors"
        >
          <PanelLeftClose className="w-4 h-4" />
          <span>Collapse Sidebar</span>
        </button>
      </div>
    </aside>
  );
}

export function SidebarToggleButton() {
  const { isSidebarOpen, toggleSidebar } = useUIStore();

  if (isSidebarOpen) return null;

  return (
    <button
      onClick={toggleSidebar}
      className="fixed top-4 left-4 z-50 p-2 rounded-md hover:bg-accent text-foreground transition-colors bg-background/50 backdrop-blur-md border border-border"
    >
      <PanelLeftOpen className="w-5 h-5" />
    </button>
  );
}
