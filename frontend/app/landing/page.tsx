'use client';

import React from 'react';
import Link from 'next/link';
import { ThemeToggleButton2 } from '@/components/theme-button';
import { Highlighter } from '@/components/ui/highlighter';
import { 
  ArrowRight, 
  Zap, 
  Brain, 
  GitBranch, 
  CheckCircle, 
  Sparkles,
  Users,
  Code,
  BarChart,
  Target
} from 'lucide-react';

export default function LandingPage() {
  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Generation',
      description: 'Transform requirements into detailed user stories and actionable tasks using advanced AI models.',
      color: 'primary'
    },
    {
      icon: GitBranch,
      title: 'GitHub Integration',
      description: 'Seamlessly sync with your repositories. Automatic status updates when PRs are created.',
      color: 'chart-2'
    },
    {
      icon: Sparkles,
      title: 'Smart Workflows',
      description: 'Automated task management with role-based permissions and intelligent routing.',
      color: 'chart-3'
    },
    {
      icon: BarChart,
      title: 'Real-time Analytics',
      description: 'Track project progress, validation scores, and team performance in real-time.',
      color: 'chart-1'
    },
    {
      icon: Code,
      title: 'Developer First',
      description: 'Built by developers, for developers. Clean APIs, webhooks, and extensible architecture.',
      color: 'accent'
    },
    {
      icon: Target,
      title: 'Quality Focused',
      description: 'Automated quality checks, validation scoring, and iterative improvement until perfect.',
      color: 'chart-4'
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Theme Toggle */}
      <ThemeToggleButton2 className="fixed bottom-5 left-5 h-8 w-8 text-primary bg-transparent z-50 cursor-pointer" />

      <div className="font-sans">
        {/* Hero Section */}
        <div className="min-h-screen flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8">
          <main className="flex flex-col gap-8 items-center text-center max-w-5xl">
            {/* Badge */}
            <div className="inline-block px-4 py-2 bg-primary/10 border border-primary/20 rounded-full">
              <span className="text-primary text-sm font-medium flex items-center gap-2">
                <Sparkles className="w-4 h-4" />
                AI-Powered Project Management
              </span>
            </div>

            {/* Headline */}
            <div className="space-y-4">
              <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-primary tracking-tighter">
                Project Management,
              </h1>
              <div className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold tracking-tighter italic">
                <Highlighter
                  strokeWidth={2}
                  padding={2}
                  iterations={2}
                  action="underline"
                  color="var(--primary)">
                  Orchestrated
                </Highlighter>
              </div>
            </div>

            {/* Subtitle */}
            <p className="text-lg sm:text-xl md:text-2xl text-muted-foreground max-w-3xl leading-relaxed italic">
              <Highlighter padding={3} color="var(--accent)">
                Tell Your Story.
              </Highlighter>{' '}
              Let Our AI Agents Handle the Rest.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 items-center mt-8">
              <Link
                href="/projects"
                className="group rounded-full transition-colors flex items-center justify-center bg-primary text-primary-foreground gap-2 hover:bg-primary/90 font-medium text-sm sm:text-base h-10 sm:h-12 px-6 sm:px-8 w-full sm:w-auto">
                Get Started
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                href="/requirements"
                className="rounded-full border border-border transition-colors flex items-center justify-center hover:bg-muted font-medium text-sm sm:text-base h-10 sm:h-12 px-6 sm:px-8 w-full sm:w-auto">
                Try AI Agent
              </Link>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-12 w-full max-w-4xl">
              {[
                { value: '10x', label: 'Faster Planning' },
                { value: '95%', label: 'Accuracy Rate' },
                { value: '500+', label: 'Tasks Generated' },
                { value: '24/7', label: 'AI Availability' }
              ].map((stat, index) => (
                <div key={index} className="text-center p-4 bg-card border border-border rounded-lg">
                  <div className="text-3xl font-bold text-primary mb-1">
                    {stat.value}
                  </div>
                  <div className="text-sm text-muted-foreground">{stat.label}</div>
                </div>
              ))}
            </div>
          </main>
        </div>

        {/* Features Section */}
        <div className="py-20 px-4 sm:px-6 lg:px-8 bg-muted/30">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-primary mb-4 tracking-tighter">
                Powerful Features
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto italic">
                Everything you need to orchestrate your development workflow
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {features.map((feature, index) => (
                <div
                  key={index}
                  className="group p-6 bg-card border border-border rounded-lg hover:border-primary hover:shadow-lg transition-all duration-200">
                  <div className="flex items-center gap-3 mb-4">
                    <div className={`w-10 h-10 bg-${feature.color}/10 rounded-lg flex items-center justify-center`}>
                      <feature.icon className={`w-5 h-5 text-${feature.color}`} />
                    </div>
                    <h3 className="font-semibold text-foreground">{feature.title}</h3>
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed italic">
                    {feature.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* How It Works Section */}
        <div className="py-20 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-primary mb-4 tracking-tighter">
                How It Works
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto italic">
                From idea to implementation in three simple steps
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              {[
                {
                  step: '01',
                  title: 'Input Requirements',
                  description: 'Describe your project in plain English or upload existing documentation. Our AI understands context.',
                  icon: Zap
                },
                {
                  step: '02',
                  title: 'AI Generation',
                  description: 'Watch as our AI generates comprehensive user stories, detailed tasks, and acceptance criteria.',
                  icon: Brain
                },
                {
                  step: '03',
                  title: 'Start Building',
                  description: 'Sync with GitHub, assign tasks, and track progress with automated workflows and real-time updates.',
                  icon: CheckCircle
                }
              ].map((item, index) => (
                <div key={index} className="relative">
                  <div className="text-6xl font-bold text-muted/20 absolute -top-4 -left-2">
                    {item.step}
                  </div>
                  <div className="relative p-6 bg-card border border-border rounded-lg">
                    <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                      <item.icon className="w-5 h-5 text-primary" />
                    </div>
                    <h3 className="text-xl font-semibold text-foreground mb-3">{item.title}</h3>
                    <p className="text-sm text-muted-foreground leading-relaxed italic">
                      {item.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="py-20 px-4 sm:px-6 lg:px-8 bg-muted/30">
          <div className="max-w-4xl mx-auto text-center">
            <div className="p-12 bg-card border border-border rounded-2xl">
              <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-primary mb-6 tracking-tighter">
                Ready to Get Started?
              </h2>
              <p className="text-lg text-muted-foreground mb-10 max-w-2xl mx-auto italic">
                Join teams building better software faster with AI-powered project management
              </p>
              <div className="flex flex-col sm:flex-row gap-4 items-center justify-center">
                <Link
                  href="/projects"
                  className="group rounded-full transition-colors flex items-center justify-center bg-primary text-primary-foreground gap-2 hover:bg-primary/90 font-medium text-sm sm:text-base h-10 sm:h-12 px-6 sm:px-8 w-full sm:w-auto">
                  Start Building Now
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </Link>
                <a
                  href="https://github.com/Noob4Eternity/Jod-Capstone"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="rounded-full border border-border transition-colors flex items-center justify-center hover:bg-muted font-medium text-sm sm:text-base h-10 sm:h-12 px-6 sm:px-8 w-full sm:w-auto">
                  View on GitHub
                </a>
              </div>
              <p className="text-muted-foreground text-sm mt-6 italic">
                Free forever for small teams • No credit card required
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="py-12 px-4 sm:px-6 lg:px-8 border-t border-border">
          <div className="max-w-7xl mx-auto">
            <div className="grid md:grid-cols-4 gap-8 mb-8">
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center">
                    <Sparkles className="w-5 h-5 text-primary" />
                  </div>
                  <span className="text-lg font-bold text-foreground">orchestrate.ai</span>
                </div>
                <p className="text-sm text-muted-foreground italic">
                  AI-powered project management for modern teams
                </p>
              </div>

              <div>
                <h4 className="font-semibold text-foreground mb-3">Product</h4>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li><Link href="/projects" className="hover:text-primary transition-colors">Projects</Link></li>
                  <li><Link href="/requirements" className="hover:text-primary transition-colors">AI Agent</Link></li>
                  <li><Link href="/menu" className="hover:text-primary transition-colors">Features</Link></li>
                </ul>
              </div>

              <div>
                <h4 className="font-semibold text-foreground mb-3">Resources</h4>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li><a href="https://github.com/Noob4Eternity/Jod-Capstone" target="_blank" rel="noopener noreferrer" className="hover:text-primary transition-colors">GitHub</a></li>
                  <li><a href="#" className="hover:text-primary transition-colors">Documentation</a></li>
                  <li><a href="#" className="hover:text-primary transition-colors">API</a></li>
                </ul>
              </div>

              <div>
                <h4 className="font-semibold text-foreground mb-3">Company</h4>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li><a href="#" className="hover:text-primary transition-colors">About</a></li>
                  <li><a href="#" className="hover:text-primary transition-colors">Contact</a></li>
                  <li><a href="#" className="hover:text-primary transition-colors">Privacy</a></li>
                </ul>
              </div>
            </div>

            <div className="pt-8 border-t border-border flex flex-col md:flex-row items-center justify-between gap-4">
              <p className="text-sm text-muted-foreground">
                © 2025 orchestrate.ai. Built with Next.js and TypeScript.
              </p>
              <div className="flex items-center gap-4">
                <a href="https://github.com/Noob4Eternity/Jod-Capstone" target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-primary transition-colors">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd"></path></svg>
                </a>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
