"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

interface FloatingNavProps {
  currentPage?: string;
  onNavigate?: (page: string) => void;
}

export function FloatingNav({ currentPage, onNavigate }: FloatingNavProps = {}) {
  const pathname = usePathname();
  const isClientSideNav = !!onNavigate;
  const activePage = currentPage || pathname;

  const navItems = [
    {
      name: "Menu",
      page: "menu",
      href: "/menu",
      icon: (
        <svg
          className="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
          />
        </svg>
      ),
    },
    {
      name: "Projects",
      page: "projects",
      href: "/projects",
      icon: (
        <svg
          className="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
          />
        </svg>
      ),
    },
    {
      name: "AI Agent",
      page: "requirements",
      href: "/requirements",
      icon: (
        <svg
          className="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13 10V3L4 14h7v7l9-11h-7z"
          />
        </svg>
      ),
    },
  ];

  return (
    <nav className="absolute top-6 left-1/2 -translate-x-1/2 z-40">
      <div className="flex items-center gap-2 px-4 py-2 bg-card/80 backdrop-blur-md border border-border rounded-full shadow-lg">
        {navItems.map((item) => {
          const isActive = isClientSideNav ? activePage === item.page : activePage === item.href;

          if (isClientSideNav && onNavigate) {
            // Client-side navigation (no page reload)
            return (
              <button
                key={item.page}
                onClick={() => onNavigate(item.page)}
                className={`
                  flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200
                  ${
                    isActive
                      ? "bg-primary text-primary-foreground shadow-sm"
                      : "text-muted-foreground hover:text-foreground hover:bg-muted"
                  }
                `}>
                {item.icon}
                <span className="hidden sm:inline">{item.name}</span>
              </button>
            );
          }

          // Server-side navigation with Link
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`
                flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200
                ${
                  isActive
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted"
                }
              `}>
              {item.icon}
              <span className="hidden sm:inline">{item.name}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
