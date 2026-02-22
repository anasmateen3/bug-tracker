import { Link } from 'react-router-dom';
import { Bug, CheckCircle, Users, BarChart3 } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      {/* Header */}
      <header className="border-b backdrop-blur-sm bg-background/80 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Bug className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold tracking-tight">BugTracker</span>
          </div>
          <div className="flex gap-3">
            <Link to="/login">
              <Button variant="ghost" data-testid="login-btn">Login</Button>
            </Link>
            <Link to="/register">
              <Button data-testid="register-btn">Get Started</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-6 py-20 md:py-32 text-center">
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight mb-6">
          Track Bugs.
          <br />
          <span className="text-primary">Ship Faster.</span>
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-10">
          The modern bug tracker for agile teams. Manage projects, assign tasks, and collaborate seamlessly with your team.
        </p>
        <Link to="/register">
          <Button size="lg" className="text-base" data-testid="hero-get-started-btn">
            Get Started Free
          </Button>
        </Link>
      </section>

      {/* Features */}
      <section className="container mx-auto px-6 py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-card rounded-lg p-6 border">
            <CheckCircle className="h-10 w-10 text-primary mb-4" />
            <h3 className="text-xl font-semibold mb-2">Kanban Boards</h3>
            <p className="text-muted-foreground text-sm">
              Drag-and-drop tickets across To Do, In Progress, and Done columns for visual workflow management.
            </p>
          </div>
          <div className="bg-card rounded-lg p-6 border">
            <Users className="h-10 w-10 text-primary mb-4" />
            <h3 className="text-xl font-semibold mb-2">Team Collaboration</h3>
            <p className="text-muted-foreground text-sm">
              Assign tickets, add comments, and keep everyone in sync with real-time updates.
            </p>
          </div>
          <div className="bg-card rounded-lg p-6 border">
            <BarChart3 className="h-10 w-10 text-primary mb-4" />
            <h3 className="text-xl font-semibold mb-2">Project Insights</h3>
            <p className="text-muted-foreground text-sm">
              Track progress with filters, search, and priority levels to stay on top of every bug.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
