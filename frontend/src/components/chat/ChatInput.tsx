"use client";

import { useRef, useState, useEffect } from "react";
import { Paperclip, Mic, ArrowUp } from "lucide-react";
import { cn } from "@/lib/utils";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading?: boolean;
}

export function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + "px";
    }
  }, [input]);

  const handleSend = () => {
    if (input.trim() && !isLoading) {
      onSend(input.trim());
      setInput("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="relative bg-card border border-border rounded-2xl p-2 focus-within:ring-2 focus-within:ring-primary/50 focus-within:border-primary/50 transition-all shadow-sm">
      <textarea
        ref={textareaRef}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        className="w-full bg-transparent resize-none border-0 focus:ring-0 p-2 text-sm max-h-[200px] min-h-[44px] scrollbar-thin outline-none"
        placeholder="Message AI Assistant..."
        rows={1}
      />
      <div className="flex items-center justify-between px-2 pt-2 border-t border-border/50 mt-2">
        <div className="flex items-center gap-1">
          <Tooltip>
            <TooltipTrigger className="p-2 text-muted-foreground hover:text-foreground hover:bg-secondary rounded-lg transition-colors flex items-center justify-center"><Paperclip className="w-4 h-4" /></TooltipTrigger>
            <TooltipContent>Attach file</TooltipContent>
          </Tooltip>
          
          <Tooltip>
            <TooltipTrigger className="p-2 text-muted-foreground hover:text-foreground hover:bg-secondary rounded-lg transition-colors flex items-center justify-center"><Mic className="w-4 h-4" /></TooltipTrigger>
            <TooltipContent>Voice message</TooltipContent>
          </Tooltip>
        </div>
        
        <button
          onClick={handleSend}
          disabled={!input.trim() || isLoading}
          className={cn(
            "p-2 rounded-lg transition-all duration-200 flex items-center justify-center",
            input.trim() && !isLoading
              ? "bg-primary text-primary-foreground hover:bg-primary/90 shadow-md"
              : "bg-muted text-muted-foreground cursor-not-allowed"
          )}
        >
          <ArrowUp className="w-4 h-4 stroke-[3]" />
        </button>
      </div>
    </div>
  );
}
