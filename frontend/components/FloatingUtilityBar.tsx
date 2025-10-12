"use client";

import { ThemeToggleButton2 } from "@/components/theme-button";
import { SignOutButton } from "@/components/SignOutButton";

export function FloatingUtilityBar() {
  return (
    <div className="absolute top-6 right-6 z-40">
      <div className="flex items-center gap-3 px-4 py-2 bg-card/80 backdrop-blur-md border border-border rounded-full shadow-lg">
        <ThemeToggleButton2 className="h-8 w-8 text-primary bg-transparent cursor-pointer" />
        <div className="w-px h-6 bg-border" /> {/* Divider */}
        <SignOutButton
          variant="ghost"
          size="sm"
        />
      </div>
    </div>
  );
}
