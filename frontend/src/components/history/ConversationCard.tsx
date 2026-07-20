"use client";

import { useState } from "react";
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
  onSelect?: () => void;
  onDelete?: () => void;
  onRename?: (newTitle: string) => void;
}

export function ConversationCard({
  conversation,
  onSelect,
  onDelete,
  onRename,
}: ConversationCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(conversation.title);

  const date = new Date(conversation.updatedAt).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
  });

  const handleRename = () => {
    if (editTitle.trim() && editTitle !== conversation.title) {
      onRename?.(editTitle.trim());
    }
    setIsEditing(false);
  };

  return (
    <div
      className="group relative bg-card hover:bg-accent border border-border rounded-xl p-4 transition-colors cursor-pointer shadow-sm"
      onClick={() => !isEditing && onSelect?.()}
    >
      <div className="flex items-start justify-between mb-2">
        {isEditing ? (
          <input
            type="text"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            onBlur={handleRename}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleRename();
              if (e.key === "Escape") setIsEditing(false);
            }}
            autoFocus
            className="font-semibold text-foreground bg-transparent border-b border-primary outline-none pr-6 w-full"
            onClick={(e) => e.stopPropagation()}
          />
        ) : (
          <h3 className="font-semibold text-foreground truncate pr-6 flex items-center gap-2">
            {conversation.isPinned && (
              <Pin className="w-3.5 h-3.5 text-primary rotate-45" />
            )}
            {conversation.title}
          </h3>
        )}

        <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
          <DropdownMenu>
            <DropdownMenuTrigger
              className="p-1 rounded-md hover:bg-background text-muted-foreground transition-colors outline-none"
              onClick={(e) => e.stopPropagation()}
            >
              <MoreHorizontal className="w-4 h-4" />
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-40">
              <DropdownMenuItem
                className="cursor-pointer gap-2"
                onClick={(e) => {
                  e.stopPropagation();
                  setIsEditing(true);
                }}
              >
                <Edit2 className="w-4 h-4 text-muted-foreground" /> Rename
              </DropdownMenuItem>
              <DropdownMenuItem className="cursor-pointer gap-2">
                <Pin className="w-4 h-4 text-muted-foreground" />{" "}
                {conversation.isPinned ? "Unpin" : "Pin"}
              </DropdownMenuItem>
              <DropdownMenuItem className="cursor-pointer gap-2">
                <Archive className="w-4 h-4 text-muted-foreground" /> Archive
              </DropdownMenuItem>
              <DropdownMenuItem
                className="cursor-pointer gap-2 text-destructive focus:bg-destructive/10 focus:text-destructive"
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete?.();
                }}
              >
                <Trash className="w-4 h-4" /> Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {conversation.preview && (
        <p className="text-sm text-muted-foreground line-clamp-2 mb-4 leading-relaxed">
          {conversation.preview}
        </p>
      )}

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {conversation.tags.map((tag) => (
            <span
              key={tag}
              className="text-[10px] font-medium px-2 py-0.5 bg-secondary text-secondary-foreground rounded-full"
            >
              {tag}
            </span>
          ))}
        </div>
        <span className="text-[11px] text-muted-foreground font-medium">
          {date}
        </span>
      </div>
    </div>
  );
}
