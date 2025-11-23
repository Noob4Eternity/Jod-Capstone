"use client";

import Folder from "@/components/Folder";
import Navbar from "@/components/Navbar";
import StaggeredMenu from "@/components/StaggeredMenu";
import { ThemeToggleButton2 } from "@/components/theme-button";
import { Highlighter } from "@/components/ui/highlighter";

export default function Home() {
  const menuItems = [
    { label: "Menu", ariaLabel: "Go to home page", link: "/menu" },
    { label: "Projects", ariaLabel: "View all Projects", link: "/projects" },
    { label: "Agent", ariaLabel: "View our agent", link: "/requirements" },
  ];

  const socialItems = [
    { label: "Twitter", link: "https://twitter.com" },
    { label: "GitHub", link: "https://github.com" },
    { label: "LinkedIn", link: "https://linkedin.com" },
  ];

  return (
    <div className="min-h-screen px-4 sm:px-6 lg:px-8 bg-muted/90">
      <ThemeToggleButton2 className="fixed bottom-5 left-5 h-8 w-8 text-primary bg-transparent z-50 cursor-pointer" />

      <Navbar />
      <div
        style={{ height: "100vh" }}
        className="fixed top-0 right-0 w-screen  ">
        <StaggeredMenu
          position="right"
          items={menuItems}
          socialItems={socialItems}
          displaySocials={true}
          displayItemNumbering={true}
          menuButtonColor="#fff"
          openMenuButtonColor="#fff"
          changeMenuColorOnOpen={true}
          colors={["#B19EEF", "#5227FF"]}
          accentColor="#ff6b6b"
          onMenuOpen={() => console.log("Menu opened")}
          onMenuClose={() => console.log("Menu closed")}
        />
      </div>
      <div className="flex items-start justify-center ">
        <Folder
          size={1}
          className="custom-folder mt-12 sm:mt-16 md:mt-20 lg:mt-24"
        />
      </div>

      <div className="flex flex-col items-center justify-center mt-1 sm:mt-8 md:mt-4 px-4">
        <div className="text-primary text-2xl sm:text-3xl md:text-5xl lg:text-6xl font-bold text-center tracking-tighter">
          Project Management,
        </div>
        <div className="italic text-2xl sm:text-3xl md:text-5xl lg:text-6xl font-bold text-center tracking-tighter">
          <Highlighter
            strokeWidth={2}
            padding={2}
            iterations={2}
            action="underline"
            color="var(--primary)">
            Simplified
          </Highlighter>
        </div>
      </div>
      <div className="flex items-center justify-center mt-2 sm:mt-4 md:mt-6 px-6">
        <p className="italic text-secondary--foreground text-center text-base sm:text-lg md:text-xl lg:text-2xl max-w-3xl leading-relaxed">
          <Highlighter
            opacity={0.2}
            padding={3}
            animationDuration={1200}
            color="var(--primary)">
            Tell Your Story.
          </Highlighter>{" "}
          Let Our System Manage the Rest.
        </p>
      </div>
      <div></div>
    </div>
  );
}
