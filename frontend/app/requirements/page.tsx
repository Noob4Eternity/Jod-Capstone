"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ThemeToggleButton2 } from "@/components/theme-button"; // ✅ dark mode toggle

export default function Agents() {
  const [requirements, setRequirements] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [maxIterations, setMaxIterations] = useState(3);
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<any>(null);
  const [error, setError] = useState("");

  const [projectTitle, setProjectTitle] = useState("");
  const [industry, setIndustry] = useState("");
  const [teamSize, setTeamSize] = useState<number | "">("");
  const [budget, setBudget] = useState<number | "">("");
  const [timeline, setTimeline] = useState("");
  const [priority, setPriority] = useState("");
  const [techStack, setTechStack] = useState("");

  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    setResponse(null);

    // Client-side validation
    const hasText = requirements && requirements.trim();
    const hasFile = file !== null;

    if (!hasText && !hasFile) {
      setError("Please provide either requirements text or upload a PDF file.");
      setIsLoading(false);
      return;
    }

    const projectContext: any = {};
    if (projectTitle) projectContext.title = projectTitle;
    if (industry) projectContext.industry = industry;
    if (teamSize !== "") projectContext.team_size = teamSize;
    if (budget !== "") projectContext.budget = budget;
    if (timeline) projectContext.timeline = timeline;
    if (priority) projectContext.priority = priority;
    if (techStack) projectContext.tech_stack = techStack.split(",").map((s: string) => s.trim());

    const formData = new FormData();
    if (requirements) formData.append("requirements", requirements);
    if (file) formData.append("files", file);
    if (Object.keys(projectContext).length > 0) {
      formData.append("project_context", JSON.stringify(projectContext));
    }
    formData.append("max_iterations", maxIterations.toString());

    try {
      const res = await fetch("http://localhost:8000/generate", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`HTTP error! status: ${res.status} - ${errorText}`);
      }

      const data = await res.json();

      if (data.success && data.project_id) {
        router.push(`/board/${data.project_id}`);
        return;
      }
      setResponse(data);
    } catch (err: any) {
      setError(err.message || "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      {/* ✅ Dark mode toggle */}
      <ThemeToggleButton2 className="fixed bottom-5 left-5 h-8 w-8 text-primary bg-transparent z-50 cursor-pointer" />

      <div className="font-sans grid grid-rows-[2px_1fr_2px] items-center justify-items-center min-h-screen pb-5 gap-10">
        <main className="flex flex-col gap-[24px] row-start-2 items-center sm:items-start w-full max-w-3xl">
          {/* Header */}
          <div className="text-center sm:text-left">
            <h1 className="text-4xl font-bold text-primary mb-1">
              AI Agents - Generate User Stories
            </h1>
            <p className="text-md text-secondary-foreground italic mb-1">
              Input your project requirements and let AI generate stories and tasks.
            </p>
          </div>

          {/* Form Card */}
          <div className="w-full p-6 bg-card border border-border rounded-lg shadow-sm">
            <form
              onSubmit={handleSubmit}
              className="space-y-6">
              {/* Project Title */}
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Project Title
                </label>
                <input
                  type="text"
                  value={projectTitle}
                  onChange={(e) => setProjectTitle(e.target.value)}
                  placeholder="Enter a descriptive title"
                  className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              {/* Requirements */}
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Client Requirements
                </label>
                <textarea
                  value={requirements}
                  onChange={(e) => setRequirements(e.target.value)}
                  placeholder="Describe your requirements..."
                  rows={4}
                  className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              {/* File Upload + Iterations */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Upload Documentation (PDF or DOCX)
                  </label>
                  <input
                    type="file"
                    accept=".pdf,.docx"
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                    className="w-full text-sm text-muted-foreground file:mr-4 file:py-2 file:px-4 
                               file:rounded-md file:border-0 file:bg-primary file:text-primary-foreground 
                               hover:file:bg-primary/80 cursor-pointer"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Max Iterations
                  </label>
                  <input
                    type="number"
                    value={maxIterations}
                    onChange={(e) => setMaxIterations(Number(e.target.value))}
                    min={1}
                    max={10}
                    className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>

              {/* Context Section */}
              <div className="space-y-4">
                <label className="block text-sm font-medium text-foreground">
                  Project Context (Optional)
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {/* Industry */}
                  <input
                    type="text"
                    value={industry}
                    onChange={(e) => setIndustry(e.target.value)}
                    placeholder="Industry (e.g. Healthcare)"
                    className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                  {/* Team Size */}
                  <input
                    type="number"
                    value={teamSize}
                    onChange={(e) => setTeamSize(e.target.value ? Number(e.target.value) : "")}
                    placeholder="Team Size"
                    className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                  {/* Budget */}
                  <input
                    type="number"
                    value={budget}
                    onChange={(e) => setBudget(e.target.value ? Number(e.target.value) : "")}
                    placeholder="Budget ($)"
                    className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                  {/* Timeline */}
                  <input
                    type="text"
                    value={timeline}
                    onChange={(e) => setTimeline(e.target.value)}
                    placeholder="Timeline (e.g. 3 months)"
                    className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                  {/* Priority */}
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value)}
                    className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary">
                    <option value="">Priority</option>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                  {/* Tech Stack */}
                  <input
                    type="text"
                    value={techStack}
                    onChange={(e) => setTechStack(e.target.value)}
                    placeholder="Tech Stack (comma separated)"
                    className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-4 items-center flex-col sm:flex-row">
                <button
                  type="submit"
                  disabled={isLoading}
                  className="rounded-full transition-colors flex items-center justify-center 
                             bg-primary text-primary-foreground hover:bg-primary/80 
                             font-medium text-sm sm:text-base h-10 sm:h-12 px-6 disabled:opacity-50">
                  {isLoading ? "Generating..." : "Generate User Stories"}
                </button>

                <Link
                  href="/menu"
                  className="rounded-full border border-border transition-colors flex items-center justify-center 
                             hover:bg-muted font-medium text-sm sm:text-base h-10 sm:h-12 px-6">
                  Back to Menu
                </Link>
              </div>
            </form>
          </div>

          {/* Error + Response Cards */}
          {error && (
            <div className="w-full p-4 bg-destructive/20 border border-destructive text-destructive rounded-md">
              <strong>Error:</strong> {error}
            </div>
          )}
          {response && (
            <div className="w-full p-6 bg-card border border-border rounded-lg">
              <h3 className="font-semibold text-foreground mb-2">Generation Successful!</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Project <strong>{response.project_id}</strong> generated with{" "}
                {response.user_stories?.length || 0} stories.
              </p>
              <div className="flex gap-2 flex-wrap">
                <Link
                  href={`/board/${response.project_id}`}
                  className="btn-primary">
                  View Project Board
                </Link>
                <Link
                  href="/projects"
                  className="btn-secondary">
                  View All Projects
                </Link>
                <Link
                  href="/requirements"
                  className="btn-muted">
                  Generate Another
                </Link>
              </div>
            </div>
          )}
        </main>

        <footer className="row-start-3 flex gap-4 flex-wrap items-center justify-center">
          <div className="text-sm text-muted-foreground">
            Built with Next.js, TypeScript, and Tailwind CSS
          </div>
        </footer>
      </div>
    </div>
  );
}
