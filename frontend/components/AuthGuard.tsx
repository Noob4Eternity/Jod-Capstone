"use client";

import { ReactNode, useEffect, useMemo, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";

const PUBLIC_PATHS = new Set(["/login"]);

interface AuthGuardProps {
  children: ReactNode;
}

export function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [isChecking, setIsChecking] = useState(true);

  const isPublicRoute = useMemo(() => {
    if (!pathname) return false;
    if (pathname === "/") {
      return false;
    }
    return PUBLIC_PATHS.has(pathname);
  }, [pathname]);

  useEffect(() => {
    let isMounted = true;
    const ensureSession = async () => {
      if (isPublicRoute) {
        if (isMounted) {
          setIsChecking(false);
        }
        return;
      }

      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (!session) {
        const redirectTarget = pathname || "/";
        router.replace(`/login?redirect=${encodeURIComponent(redirectTarget)}`);
      }

      if (isMounted) {
        setIsChecking(false);
      }
    };

    ensureSession();

    const { data } = supabase.auth.onAuthStateChange((event, session) => {
      if (!isMounted) return;

      if (!session) {
        router.replace("/login");
        return;
      }

      if (pathname === "/login") {
        router.replace("/");
      }
    });

    return () => {
      isMounted = false;
      data.subscription.unsubscribe();
    };
  }, [isPublicRoute, pathname, router]);

  if (isPublicRoute) {
    return <>{children}</>;
  }

  if (isChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4" />
          <p className="text-gray-600">Validating session...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
