import { DndContext, DragOverlay, closestCorners, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { useState } from 'react';
import KanbanColumn from './KanbanColumn';
import TicketCard from './TicketCard';

export default function KanbanBoard({ tickets, onTicketClick, onStatusChange, loading }) {
  const [activeTicket, setActiveTicket] = useState(null);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  );

  const columns = [
    { id: 'todo', title: 'To Do', color: 'text-blue-500' },
    { id: 'inprogress', title: 'In Progress', color: 'text-amber-500' },
    { id: 'done', title: 'Done', color: 'text-green-500' },
  ];

  const getTicketsByStatus = (status) => {
    return tickets.filter((ticket) => ticket.status === status);
  };

  const handleDragStart = (event) => {
    const ticket = tickets.find((t) => t.id === event.active.id);
    setActiveTicket(ticket);
  };

  const handleDragEnd = (event) => {
    const { active, over } = event;
    setActiveTicket(null);

    if (!over) return;

    const ticketId = active.id;
    const newStatus = over.id;

    const ticket = tickets.find((t) => t.id === ticketId);
    if (ticket && ticket.status !== newStatus) {
      onStatusChange(ticketId, newStatus);
    }
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {columns.map((column) => (
          <div key={column.id} className="bg-muted/30 rounded-lg p-4 h-[600px] animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCorners}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4" data-testid="kanban-board">
        {columns.map((column) => {
          const columnTickets = getTicketsByStatus(column.id);
          return (
            <KanbanColumn
              key={column.id}
              id={column.id}
              title={column.title}
              color={column.color}
              count={columnTickets.length}
            >
              <SortableContext items={columnTickets.map((t) => t.id)} strategy={verticalListSortingStrategy}>
                <div className="space-y-3">
                  {columnTickets.map((ticket) => (
                    <TicketCard
                      key={ticket.id}
                      ticket={ticket}
                      onClick={() => onTicketClick(ticket)}
                    />
                  ))}
                </div>
              </SortableContext>
            </KanbanColumn>
          );
        })}
      </div>

      <DragOverlay>
        {activeTicket ? (
          <div className="opacity-50">
            <TicketCard ticket={activeTicket} isDragging />
          </div>
        ) : null}
      </DragOverlay>
    </DndContext>
  );
}
