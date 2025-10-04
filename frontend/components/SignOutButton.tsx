"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";
import { LogOut } from "lucide-react";
import clsx from "clsx";

interface SignOutButtonProps {
  className?: string;
  variant?: "solid" | "ghost";
  size?: "sm" | "md";
}

export function SignOutButton({
  className,
  variant = "ghost",
  size = "sm",
}: SignOutButtonProps) {
  const router = useRouter();
  const [isSigningOut, setIsSigningOut] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSignOut = async () => {
    if (isSigningOut) return;

    setIsSigningOut(true);
    setError(null);

    const { error: signOutError } = await supabase.auth.signOut();

    if (signOutError) {
      console.error("Failed to sign out", signOutError);
      setError("Sign out failed. Please try again.");
      setIsSigningOut(false);
      return;
    }

    router.replace("/login");
    router.refresh();
  };

  const baseStyles = "inline-flex items-center gap-2 rounded-lg font-medium transition focus:outline-none focus:ring-2 focus:ring-offset-2";
  const sizeStyles = size === "sm" ? "px-3 py-1.5 text-sm" : "px-4 py-2 text-base";
  const variantStyles =
    variant === "solid"
      ? "bg-slate-900 text-white hover:bg-slate-800 focus:ring-slate-500"
      : "bg-white/5 text-slate-200 border border-white/10 hover:bg-white/10 focus:ring-slate-300";

  return (
    <div className={clsx("flex flex-col items-stretch", className)}>
      <button
        type="button"
        onClick={handleSignOut}
        disabled={isSigningOut}
        className={clsx(baseStyles, sizeStyles, variantStyles,
          "disabled:cursor-not-allowed disabled:opacity-60")}
      >
        <LogOut className={clsx(size === "sm" ? "h-4 w-4" : "h-5 w-5")}
        />
        <span>{isSigningOut ? "Signing out..." : "Sign out"}</span>
      </button>
      {error && (
        <span className="mt-1 text-xs text-rose-200" role="alert">
          {error}
        </span>
      )}
    </div>
  );
}
