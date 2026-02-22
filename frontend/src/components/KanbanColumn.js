import { useDroppable } from '@dnd-kit/core';

export default function KanbanColumn({ id, title, color, count, children }) {
  const { setNodeRef, isOver } = useDroppable({ id });

  return (
    <div
      ref={setNodeRef}
      className={`bg-muted/30 rounded-lg p-4 min-h-[600px] transition-colors ${
        isOver ? 'ring-2 ring-primary bg-primary/5' : ''
      }`}
      data-testid={`kanban-column-${id}`}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <h3 className={`font-semibold text-sm uppercase tracking-wider ${color}`}>{title}</h3>
          <span className="text-xs font-mono bg-background px-2 py-1 rounded border">{count}</span>
        </div>
      </div>
      {children}
    </div>
  );
}
