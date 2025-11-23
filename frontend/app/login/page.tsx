"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { useRouter, useSearchParams } from "next/navigation";
import { supabase } from "@/lib/supabase";
import { useTheme } from "next-themes";
import { Sun, Moon, ShieldCheck, ArrowRight } from "lucide-react";
import { Highlighter } from "@/components/ui/highlighter";
import { cn } from "@/lib/utils";

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [infoMessage, setInfoMessage] = useState<string | null>(null);

  useEffect(() => {
    setMounted(true);
    const init = async () => {
      const { data } = await supabase.auth.getSession();
      if (data.session) {
        router.replace("/");
      }
    };

    init();
  }, [router]);

  useEffect(() => {
    const message = searchParams.get("message");
    if (message) {
      setInfoMessage(message);
    }
  }, [searchParams]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    setInfoMessage(null);

    try {
      const { error: signInError } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (signInError) {
        setError(signInError.message);
        setIsSubmitting(false);
        return;
      }

      router.replace("/");
    } catch (err) {
      console.error("Unexpected sign-in error", err);
      setError("Something went wrong. Please try again.");
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex transition-colors duration-700">
      {/* Left Side - Visual Brand */}
      <div className="hidden lg:flex lg:w-1/2 relative bg-secondary/30 items-center justify-center p-12 transition-all duration-700">
        <div className="w-full max-w-lg flex flex-col items-center text-center space-y-12">
          <div className="relative w-full h-64 lg:h-80">
            <Image
              src={
                mounted && (theme === "dark" || resolvedTheme === "dark")
                  ? "/team_2.svg"
                  : "/team_1.svg"
              }
              alt="Team Collaboration"
              fill
              className="object-contain drop-shadow-xl"
              priority
            />
          </div>

          <div className="space-y-6">
            <h1 className="text-4xl lg:text-5xl font-bold tracking-tighter text-foreground">
              Project Management,
              <br />
              <span className="italic text-primary block mt-2">
                <Highlighter
                  strokeWidth={3}
                  padding={4}
                  iterations={2}
                  action="underline"
                  color="var(--primary)">
                  Simplified
                </Highlighter>
              </span>
            </h1>

            <p className="text-lg text-muted-foreground max-w-md mx-auto leading-relaxed">
              Tell Your Story. Let Our System Manage the Rest.
            </p>
          </div>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="flex-1 flex flex-col items-center justify-center p-6 sm:p-10 relative">
        {/* Theme Toggle */}
        <div className="absolute top-6 right-6">
          {mounted && (
            <button
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="p-2.5 text-muted-foreground hover:text-primary hover:bg-secondary/80 rounded-full transition-all duration-300 border border-transparent hover:border-border"
              title="Toggle theme">
              {theme === "dark" ? <Sun size={20} /> : <Moon size={20} />}
            </button>
          )}
        </div>

        <div className="w-full max-w-md space-y-8 bg-card/50 backdrop-blur-sm p-8 rounded-3xl border border-border/40 shadow-2xl shadow-black/5">
          <div className="space-y-2 text-center">
            <h2 className="text-3xl font-bold tracking-tight text-foreground">Welcome Back</h2>
            <p className="text-sm text-muted-foreground">
              Enter your credentials to access your workspace
            </p>
          </div>

          {infoMessage && (
            <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-600 dark:text-emerald-400 flex items-center gap-2">
              <ShieldCheck size={16} />
              {infoMessage}
            </div>
          )}

          {error && (
            <div className="rounded-xl border border-destructive/20 bg-destructive/10 px-4 py-3 text-sm text-destructive flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-destructive" />
              {error}
            </div>
          )}

          <form
            onSubmit={handleSubmit}
            className="space-y-6">
            <div className="space-y-4">
              <div className="space-y-2">
                <label
                  htmlFor="email"
                  className="block text-sm font-semibold text-foreground/80 ml-1">
                  Email Address
                </label>
                <input
                  id="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  className="w-full rounded-xl border border-input bg-secondary/30 px-4 py-3 text-sm transition-all duration-200 focus:border-primary focus:bg-background focus:outline-none focus:ring-4 focus:ring-primary/10 hover:bg-secondary/50"
                  placeholder="name@company.com"
                />
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between ml-1">
                  <label
                    htmlFor="password"
                    className="block text-sm font-semibold text-foreground/80">
                    Password
                  </label>
                  <Link
                    href="https://app.supabase.com/auth"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs font-medium text-primary hover:text-primary/80 hover:underline transition-colors">
                    Forgot password?
                  </Link>
                </div>
                <input
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  className="w-full rounded-xl border border-input bg-secondary/30 px-4 py-3 text-sm transition-all duration-200 focus:border-primary focus:bg-background focus:outline-none focus:ring-4 focus:ring-primary/10 hover:bg-secondary/50"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full group relative overflow-hidden rounded-xl bg-primary px-4 py-3.5 text-sm font-bold text-primary-foreground shadow-lg shadow-primary/25 transition-all duration-300 hover:shadow-primary/40 hover:scale-[1.02] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60">
              <span className="relative z-10 flex items-center justify-center gap-2">
                {isSubmitting ? (
                  <>
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                    Signing in...
                  </>
                ) : (
                  <>
                    Sign In
                    <ArrowRight
                      size={16}
                      className="group-hover:translate-x-1 transition-transform"
                    />
                  </>
                )}
              </span>
              <div className="absolute inset-0 -z-10 bg-gradient-to-r from-white/0 via-white/20 to-white/0 opacity-0 transition-opacity duration-500 group-hover:animate-shimmer" />
            </button>
          </form>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t border-border/50" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-background px-2 text-muted-foreground font-medium">
                New to the platform?
              </span>
            </div>
          </div>

          <div className="text-center">
            <p className="text-sm text-muted-foreground">
              Contact your administrator to request access.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
