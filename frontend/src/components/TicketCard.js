import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { AlertCircle, ArrowUp, ArrowDown, Minus, AlertTriangle, MessageSquare, Paperclip } from 'lucide-react';

export default function TicketCard({ ticket, onClick, isDragging = false }) {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id: ticket.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const priorityConfig = {
    low: { icon: ArrowDown, color: 'text-blue-500', bg: 'bg-blue-500/10' },
    medium: { icon: Minus, color: 'text-amber-500', bg: 'bg-amber-500/10' },
    high: { icon: ArrowUp, color: 'text-orange-500', bg: 'bg-orange-500/10' },
    critical: { icon: AlertCircle, color: 'text-red-500', bg: 'bg-red-500/10' },
  };

  const priority = priorityConfig[ticket.priority] || priorityConfig.medium;
  const PriorityIcon = priority.icon;

  const getInitials = (name) => {
    if (!name) return '?';
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <Card
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      onClick={onClick}
      className={`p-4 cursor-pointer hover:shadow-md transition-all bg-card border ${
        isDragging ? 'opacity-50' : ''
      }`}
      data-testid={`ticket-card-${ticket.id}`}
    >
      <div className="space-y-3">
        <div className="flex items-start justify-between gap-2">
          <h4 className="font-medium text-sm leading-tight line-clamp-2">{ticket.title}</h4>
          <div className={`p-1 rounded ${priority.bg}`}>
            <PriorityIcon className={`h-3 w-3 ${priority.color}`} />
          </div>
        </div>

        {ticket.description && (
          <p className="text-xs text-muted-foreground line-clamp-2">{ticket.description}</p>
        )}

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {ticket.assignee_id && (
              <Avatar className="h-6 w-6">
                <AvatarFallback className="text-xs bg-primary/10 text-primary">
                  {getInitials(ticket.assignee_name)}
                </AvatarFallback>
              </Avatar>
            )}
          </div>
          
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            {ticket.attachments && ticket.attachments.length > 0 && (
              <div className="flex items-center gap-1">
                <Paperclip className="h-3 w-3" />
                <span>{ticket.attachments.length}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </Card>
  );
}
