import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import Layout from '@/components/Layout';
import KanbanBoard from '@/components/KanbanBoard';
import CreateTicketDialog from '@/components/CreateTicketDialog';
import TicketDetailDialog from '@/components/TicketDetailDialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Plus, Search, Filter } from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function ProjectPage() {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [tickets, setTickets] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterAssignee, setFilterAssignee] = useState('all');
  const [filterPriority, setFilterPriority] = useState('all');

  useEffect(() => {
    fetchProject();
    fetchTickets();
    fetchUsers();
  }, [projectId]);

  useEffect(() => {
    fetchTickets();
  }, [searchQuery, filterStatus, filterAssignee, filterPriority]);

  const fetchProject = async () => {
    try {
      const response = await axios.get(`${API}/projects/${projectId}`);
      setProject(response.data);
    } catch (error) {
      toast.error('Failed to fetch project');
    }
  };

  const fetchTickets = async () => {
    try {
      const params = new URLSearchParams({ project_id: projectId });
      if (searchQuery) params.append('search', searchQuery);
      if (filterStatus !== 'all') params.append('status', filterStatus);
      if (filterAssignee !== 'all') params.append('assignee_id', filterAssignee);
      
      const response = await axios.get(`${API}/tickets?${params.toString()}`);
      let filteredTickets = response.data;
      
      if (filterPriority !== 'all') {
        filteredTickets = filteredTickets.filter(t => t.priority === filterPriority);
      }
      
      setTickets(filteredTickets);
    } catch (error) {
      toast.error('Failed to fetch tickets');
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API}/users`);
      setUsers(response.data);
    } catch (error) {
      console.error('Failed to fetch users');
    }
  };

  const handleTicketClick = (ticket) => {
    setSelectedTicket(ticket);
  };

  const handleTicketUpdate = async () => {
    await fetchTickets();
    setSelectedTicket(null);
  };

  const handleStatusChange = async (ticketId, newStatus) => {
    try {
      await axios.put(`${API}/tickets/${ticketId}`, { status: newStatus });
      await fetchTickets();
      toast.success('Ticket status updated');
    } catch (error) {
      toast.error('Failed to update ticket status');
    }
  };

  const clearFilters = () => {
    setSearchQuery('');
    setFilterStatus('all');
    setFilterAssignee('all');
    setFilterPriority('all');
  };

  if (!project) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6" data-testid="project-page">
        {/* Header */}
        <div className="flex justify-between items-start">
          <div>
            <div className="flex items-center gap-3">
              <span className="font-mono text-xs px-2 py-1 bg-muted rounded border">
                {project.key}
              </span>
              <h1 className="text-4xl font-bold tracking-tight">{project.name}</h1>
            </div>
            {project.description && (
              <p className="text-muted-foreground text-sm mt-2">{project.description}</p>
            )}
          </div>
          <Button onClick={() => setCreateOpen(true)} data-testid="create-ticket-btn">
            <Plus className="h-4 w-4 mr-2" />
            New Ticket
          </Button>
        </div>

        {/* Filters */}
        <div className="bg-card rounded-lg border p-4">
          <div className="flex flex-wrap gap-3 items-center">
            <div className="flex-1 min-w-[200px] relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search tickets..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
                data-testid="search-input"
              />
            </div>
            
            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger className="w-[150px]" data-testid="filter-status">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="todo">To Do</SelectItem>
                <SelectItem value="inprogress">In Progress</SelectItem>
                <SelectItem value="done">Done</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={filterPriority} onValueChange={setFilterPriority}>
              <SelectTrigger className="w-[150px]" data-testid="filter-priority">
                <SelectValue placeholder="Priority" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Priority</SelectItem>
                <SelectItem value="low">Low</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="critical">Critical</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={filterAssignee} onValueChange={setFilterAssignee}>
              <SelectTrigger className="w-[150px]" data-testid="filter-assignee">
                <SelectValue placeholder="Assignee" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Members</SelectItem>
                {users.filter(u => project.members.includes(u.id)).map(user => (
                  <SelectItem key={user.id} value={user.id}>{user.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            {(searchQuery || filterStatus !== 'all' || filterPriority !== 'all' || filterAssignee !== 'all') && (
              <Button variant="outline" size="sm" onClick={clearFilters} data-testid="clear-filters-btn">
                Clear
              </Button>
            )}
          </div>
        </div>

        {/* Kanban Board */}
        <KanbanBoard
          tickets={tickets}
          onTicketClick={handleTicketClick}
          onStatusChange={handleStatusChange}
          loading={loading}
        />
      </div>

      {/* Create Ticket Dialog */}
      <CreateTicketDialog
        open={createOpen}
        onOpenChange={setCreateOpen}
        projectId={projectId}
        users={users.filter(u => project.members.includes(u.id))}
        onSuccess={fetchTickets}
      />

      {/* Ticket Detail Dialog */}
      {selectedTicket && (
        <TicketDetailDialog
          ticket={selectedTicket}
          open={!!selectedTicket}
          onOpenChange={(open) => !open && setSelectedTicket(null)}
          users={users.filter(u => project.members.includes(u.id))}
          projectKey={project.key}
          onUpdate={handleTicketUpdate}
        />
      )}
    </Layout>
  );
}
