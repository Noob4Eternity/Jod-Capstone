"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

interface RequirementsContentProps {
  standalone?: boolean;
}

export function RequirementsContent({ standalone = false }: RequirementsContentProps) {
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

      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

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
    <div className={standalone ? "max-w-7xl mx-auto pt-20" : "max-w-7xl mx-auto"}>
      {/* Header */}
      <div className="mb-10">
        <h1 className="text-4xl font-bold text-foreground">AI Agents - Generate User Stories</h1>
        <p className="text-muted-foreground italic">
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
            <label className="block text-sm font-medium text-foreground mb-2">Project Title</label>
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
              required={!file}
            />
          </div>

          {/* File Upload + Iterations */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Upload Documentation (PDF)
              </label>
              <input
                type="file"
                accept=".pdf"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="w-full text-sm text-muted-foreground file:mr-4 file:py-2 file:px-4 
                           file:rounded-md file:border-0 file:bg-primary file:text-primary-foreground 
                           hover:file:bg-primary/80 cursor-pointer"
                required={!requirements}
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
              <input
                type="text"
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                placeholder="Industry (e.g. Healthcare)"
                className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <input
                type="number"
                value={teamSize}
                onChange={(e) => setTeamSize(e.target.value ? Number(e.target.value) : "")}
                placeholder="Team Size"
                className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <input
                type="number"
                value={budget}
                onChange={(e) => setBudget(e.target.value ? Number(e.target.value) : "")}
                placeholder="Budget ($)"
                className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <input
                type="text"
                value={timeline}
                onChange={(e) => setTimeline(e.target.value)}
                placeholder="Timeline (e.g. 3 months)"
                className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
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

            {standalone && (
              <Link
                href="/menu"
                className="rounded-full border border-border transition-colors flex items-center justify-center 
                           hover:bg-muted font-medium text-sm sm:text-base h-10 sm:h-12 px-6">
                Back to Menu
              </Link>
            )}
          </div>
        </form>
      </div>

      {/* Error + Response Cards */}
      {error && (
        <div className="w-full p-4 bg-destructive/20 border border-destructive text-destructive rounded-md mt-6">
          <strong>Error:</strong> {error}
        </div>
      )}
      {response && (
        <div className="w-full p-6 bg-card border border-border rounded-lg mt-6">
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

      {/* Footer */}
      {standalone && (
        <div className="mt-12 text-center">
          <Link
            href="/menu"
            className="text-muted-foreground hover:text-foreground transition">
            ← Back to Menu
          </Link>
        </div>
      )}
    </div>
  );
}
