"use client";

import { cn } from "@/lib/utils";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

interface ChatBubbleProps {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
  isStreaming?: boolean;
}

export function ChatBubble({ role, content, timestamp, isStreaming }: ChatBubbleProps) {
  const isUser = role === "user";

  return (
    <div className={cn("flex w-full", isUser ? "justify-end" : "justify-start")}>
      <div className={cn("flex max-w-[85%] gap-4", isUser ? "flex-row-reverse" : "flex-row")}>
        {!isUser && (
          <Avatar className="w-8 h-8 mt-1 border border-border shadow-sm shrink-0">
            <AvatarFallback className="bg-primary text-primary-foreground text-xs font-bold">A</AvatarFallback>
          </Avatar>
        )}
        
        <div className="flex flex-col gap-1 min-w-0">
          <div
            className={cn(
              "px-4 py-3 rounded-2xl text-sm whitespace-pre-wrap break-words leading-relaxed",
              isUser
                ? "bg-primary text-primary-foreground rounded-tr-sm"
                : "bg-card border border-border/50 text-card-foreground shadow-sm rounded-tl-sm"
            )}
          >
            {content}
            {isStreaming && (
              <span className="inline-block w-2 h-4 ml-1 bg-current animate-pulse align-middle rounded-full" />
            )}
          </div>
          
          {timestamp && (
            <span className={cn("text-[10px] text-muted-foreground px-1", isUser ? "text-right" : "text-left")}>
              {timestamp}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
