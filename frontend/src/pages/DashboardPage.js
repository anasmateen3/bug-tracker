import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { Plus, FolderKanban, Users } from 'lucide-react';
import Layout from '@/components/Layout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function DashboardPage() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [projectKey, setProjectKey] = useState('');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await axios.get(`${API}/projects`);
      setProjects(response.data);
    } catch (error) {
      toast.error('Failed to fetch projects');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setCreating(true);
    try {
      await axios.post(`${API}/projects`, {
        name,
        description,
        key: projectKey.toUpperCase()
      });
      toast.success('Project created successfully!');
      setOpen(false);
      setName('');
      setDescription('');
      setProjectKey('');
      fetchProjects();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create project');
    } finally {
      setCreating(false);
    }
  };

  const projectThumbnails = [
    'https://images.pexels.com/photos/28428591/pexels-photo-28428591.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940',
    'https://images.pexels.com/photos/28428587/pexels-photo-28428587.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940',
    'https://images.pexels.com/photos/29546669/pexels-photo-29546669.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940',
    'https://images.pexels.com/photos/28544350/pexels-photo-28544350.png?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940'
  ];

  return (
    <Layout>
      <div className="space-y-6" data-testid="dashboard-page">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-bold tracking-tight">Projects</h1>
            <p className="text-muted-foreground text-sm mt-1">Manage and track your team's projects</p>
          </div>
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <Button data-testid="create-project-btn">
                <Plus className="h-4 w-4 mr-2" />
                New Project
              </Button>
            </DialogTrigger>
            <DialogContent data-testid="create-project-modal">
              <DialogHeader>
                <DialogTitle>Create New Project</DialogTitle>
                <DialogDescription>
                  Start a new project to track bugs and issues
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleCreate}>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Project Name</Label>
                    <Input
                      id="name"
                      placeholder="My Awesome Project"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      required
                      data-testid="project-name-input"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="key">Project Key</Label>
                    <Input
                      id="key"
                      placeholder="PROJ"
                      value={projectKey}
                      onChange={(e) => setProjectKey(e.target.value.toUpperCase())}
                      required
                      maxLength={10}
                      data-testid="project-key-input"
                    />
                    <p className="text-xs text-muted-foreground">Used for ticket IDs (e.g., PROJ-123)</p>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="description">Description</Label>
                    <Textarea
                      id="description"
                      placeholder="Brief description of the project"
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      rows={3}
                      data-testid="project-description-input"
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button type="submit" disabled={creating} data-testid="submit-project-btn">
                    {creating ? 'Creating...' : 'Create Project'}
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <Card key={i} className="animate-pulse">
                <div className="h-40 bg-muted rounded-t-lg" />
                <CardHeader>
                  <div className="h-6 bg-muted rounded w-3/4" />
                  <div className="h-4 bg-muted rounded w-1/2 mt-2" />
                </CardHeader>
              </Card>
            ))}
          </div>
        ) : projects.length === 0 ? (
          <Card className="border-dashed" data-testid="empty-state">
            <CardContent className="flex flex-col items-center justify-center py-16">
              <FolderKanban className="h-16 w-16 text-muted-foreground mb-4" />
              <h3 className="text-xl font-semibold mb-2">No projects yet</h3>
              <p className="text-muted-foreground text-sm mb-6 text-center max-w-sm">
                Create your first project to start tracking bugs and managing issues
              </p>
              <Button onClick={() => setOpen(true)} data-testid="empty-create-project-btn">
                <Plus className="h-4 w-4 mr-2" />
                Create Project
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" data-testid="projects-grid">
            {projects.map((project, index) => (
              <Link key={project.id} to={`/projects/${project.id}`} data-testid={`project-card-${project.id}`}>
                <Card className="overflow-hidden hover:shadow-lg transition-all hover:scale-[1.02]">
                  <div className="h-32 bg-gradient-to-br from-primary/20 to-primary/5 relative overflow-hidden">
                    <img
                      src={projectThumbnails[index % projectThumbnails.length]}
                      alt="Project"
                      className="w-full h-full object-cover opacity-50"
                    />
                    <div className="absolute top-3 left-3">
                      <span className="font-mono text-xs px-2 py-1 bg-background/80 backdrop-blur-sm rounded border">
                        {project.key}
                      </span>
                    </div>
                  </div>
                  <CardHeader>
                    <CardTitle className="text-xl">{project.name}</CardTitle>
                    <CardDescription className="line-clamp-2">
                      {project.description || 'No description'}
                    </CardDescription>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground pt-2">
                      <Users className="h-3 w-3" />
                      {project.members.length} {project.members.length === 1 ? 'member' : 'members'}
                    </div>
                  </CardHeader>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}
