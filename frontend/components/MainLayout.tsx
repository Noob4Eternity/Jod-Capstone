"use client";

import { useState } from "react";
import { FloatingNav } from "@/components/FloatingNav";
import { FloatingUtilityBar } from "@/components/FloatingUtilityBar";
import { RequirementsContent } from "@/components/RequirementsContent";
import ProjectsPage from "@/app/projects/page";
import MenuPage from "@/app/menu/page";

type PageView = "menu" | "projects" | "requirements";

export function MainLayout() {
  const [currentPage, setCurrentPage] = useState<PageView>("menu");

  const handleNavigate = (page: string) => {
    setCurrentPage(page as PageView);
  };

  const renderPage = () => {
    switch (currentPage) {
      case "menu":
        return (
          <div className="min-h-screen bg-background px-6 py-10 relative">
            <MenuPage />
          </div>
        );
      case "projects":
        return (
          <div className="min-h-screen bg-background px-6 py-10 relative">
            <div className="max-w-7xl mx-auto pt-20">
              <ProjectsPage />
            </div>
          </div>
        );
      case "requirements":
        return (
          <div className="min-h-screen bg-background px-6 py-10 relative">
            <RequirementsContent standalone={false} />
          </div>
        );
      default:
        return (
          <div className="min-h-screen bg-background px-6 py-10 relative">
            <MenuPage />
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-background relative">
      <FloatingNav
        currentPage={currentPage}
        onNavigate={handleNavigate}
      />
      <FloatingUtilityBar />
      <div className="px-6 py-10 pt-20">{renderPage()}</div>
    </div>
  );
}
