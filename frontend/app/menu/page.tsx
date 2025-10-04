import Image from "next/image";
import Link from "next/link";
import { ThemeToggleButton2 } from "@/components/theme-button"; // ✅ import dark mode button

export default function Menu() {
  return (
    <div>
      {/* ✅ Dark mode toggle button */}
      <ThemeToggleButton2 className="fixed bottom-5 left-5 h-8 w-8 text-primary bg-transparent z-50 cursor-pointer" />

      <div className="font-sans grid grid-rows-[2px_1fr_2px] items-center justify-items-center min-h-screen pb-5 gap-10">
        <main className="flex flex-col gap-[16px] row-start-2 items-center sm:items-start">
          {/* Header */}
          <div className="text-center sm:text-left">
            <h1 className="text-4xl font-bold text-primary mb-1">Agentic AI Project Manager</h1>
            <p className="text-md text-secondary-foreground italic mb-1">
              Intelligent project management powered by AI agents and Kanban boards
            </p>
          </div>

          {/* Cards */}
          <div className="flex flex-col gap-4 items-center sm:items-start">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 w-full max-w-2xl">
              {/* Projects Card */}
              <Link
                href="/projects"
                className="group">
                <div className="p-6 bg-card border border-border rounded-lg hover:border-primary hover:shadow-lg transition-all duration-200">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                      <svg
                        className="w-5 h-5 text-primary"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                        />
                      </svg>
                    </div>
                    <h3 className="font-semibold text-foreground">Projects</h3>
                  </div>
                  <p className="text-sm text-muted-foreground mb-4 italic ">
                    Browse and manage all your projects. View Kanban boards for each project.
                  </p>
                  <div className="text-primary text-sm font-medium group-hover:text-accent-foreground">
                    View Projects →
                  </div>
                </div>
              </Link>

              {/* AI Agents Card */}
              <Link
                href="/requirements"
                className="group">
                <div className="p-6 bg-card border border-border rounded-lg hover:border-primary hover:shadow-lg transition-all duration-200">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                      <svg
                        className="w-5 h-5 text-primary"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                        />
                      </svg>
                    </div>
                    <h3 className="font-semibold text-foreground">AI Agent</h3>
                  </div>
                  <p className="text-sm text-muted-foreground mb-4 italic">
                    Deploy intelligent agents to generate user stories and tasks from your
                    requirements.
                  </p>
                  <div className="text-primary text-sm font-medium group-hover:text-accent-foreground">
                    Generate Stories →
                  </div>
                </div>
              </Link>

              {/* Analytics Card (Disabled) */}
              <div className="p-6 bg-card border border-border rounded-lg opacity-60">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 bg-chart-3/30 rounded-lg flex items-center justify-center">
                    <svg
                      className="w-5 h-5 text-chart-3"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                      />
                    </svg>
                  </div>
                  <h3 className="font-semibold text-foreground">Analytics</h3>
                </div>
                <p className="text-sm text-muted-foreground mb-4">
                  Get insights into team productivity, project timelines, and performance metrics.
                </p>
                <div className="text-muted-foreground text-sm font-medium">Coming Soon...</div>
              </div>

              {/* Settings Card (Disabled) */}
              <div className="p-6 bg-card border border-border rounded-lg opacity-50">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 bg-foreground/10 rounded-lg flex items-center justify-center">
                    <svg
                      className="w-5 h-5 text-muted-foreground/70"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                      />
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                      />
                    </svg>
                  </div>
                  <h3 className="font-semibold text-foreground">Project Settings</h3>
                </div>
                <p className="text-sm text-muted-foreground mb-4">
                  Configure your workspace, team members, and project preferences.
                </p>
                <div className="text-muted-foreground text-sm font-medium">Coming Soon...</div>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-4 items-center flex-col sm:flex-row mt-8">
            {/* <Link
              href="/projects"
              className="rounded-full transition-colors flex items-center justify-center bg-primary text-primary-foreground gap-2 hover:bg-primary/80 font-medium text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5 sm:w-auto">
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                />
              </svg>
              View Projects
            </Link> */}

            <a
              className="rounded-full border border-border transition-colors flex items-center justify-center hover:bg-muted font-medium text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5 w-full sm:w-auto md:w-[158px]"
              href="https://github.com/Noob4Eternity/Jod-Capstone"
              target="_blank"
              rel="noopener noreferrer">
              View on GitHub
            </a>
          </div>
        </main>

        {/* Footer */}
        {/* <footer className="row-start-3 flex gap-[24px] flex-wrap items-center justify-center">
            <div className="text-sm text-muted-foreground">
              Built with Next.js, TypeScript, and Tailwind CSS
            </div>
          </footer> */}
      </div>
    </div>
  );
}
