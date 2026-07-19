"use client";

import { Conversation } from "@/services/api/chat";
import { MoreHorizontal, Pin, Trash, Edit2, Archive } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";

interface ConversationCardProps {
  conversation: Conversation;
}

export function ConversationCard({ conversation }: ConversationCardProps) {
  const date = new Date(conversation.updatedAt).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
  });

  return (
    <div className="group relative bg-card hover:bg-accent border border-border rounded-xl p-4 transition-colors cursor-pointer shadow-sm">
      <div className="flex items-start justify-between mb-2">
        <h3 className="font-semibold text-foreground truncate pr-6 flex items-center gap-2">
          {conversation.isPinned && <Pin className="w-3.5 h-3.5 text-primary rotate-45" />}
          {conversation.title}
        </h3>
        
        <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
          <DropdownMenu>
            <DropdownMenuTrigger className="p-1 rounded-md hover:bg-background text-muted-foreground transition-colors outline-none">
              <MoreHorizontal className="w-4 h-4" />
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-40">
              <DropdownMenuItem className="cursor-pointer gap-2">
                <Edit2 className="w-4 h-4 text-muted-foreground" /> Rename
              </DropdownMenuItem>
              <DropdownMenuItem className="cursor-pointer gap-2">
                <Pin className="w-4 h-4 text-muted-foreground" /> {conversation.isPinned ? "Unpin" : "Pin"}
              </DropdownMenuItem>
              <DropdownMenuItem className="cursor-pointer gap-2">
                <Archive className="w-4 h-4 text-muted-foreground" /> Archive
              </DropdownMenuItem>
              <DropdownMenuItem className="cursor-pointer gap-2 text-destructive focus:bg-destructive/10 focus:text-destructive">
                <Trash className="w-4 h-4" /> Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
      
      <p className="text-sm text-muted-foreground line-clamp-2 mb-4 leading-relaxed">
        {conversation.preview}
      </p>
      
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {conversation.tags.map((tag) => (
            <span key={tag} className="text-[10px] font-medium px-2 py-0.5 bg-secondary text-secondary-foreground rounded-full">
              {tag}
            </span>
          ))}
        </div>
        <span className="text-[11px] text-muted-foreground font-medium">{date}</span>
      </div>
    </div>
  );
}
