"use client";

import { Sidebar, SidebarToggleButton } from "./Sidebar";
import { ReactNode } from "react";

export function AppLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-background text-foreground">
      <Sidebar />
      <SidebarToggleButton />
      <main className="flex-1 flex flex-col h-full relative overflow-hidden">
        <div className="flex-1 w-full max-w-[900px] mx-auto relative h-full flex flex-col">
          {children}
        </div>
      </main>
    </div>
  );
}
