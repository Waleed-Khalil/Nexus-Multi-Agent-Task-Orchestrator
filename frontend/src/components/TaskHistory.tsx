import type { Task } from "../types";
import { StatusBadge } from "./StatusBadge";

interface TaskHistoryProps {
  tasks: Task[];
  activeTaskId: string | null;
  onSelect: (task: Task) => void;
}

export function TaskHistory({ tasks, activeTaskId, onSelect }: TaskHistoryProps) {
  if (tasks.length === 0) {
    return (
      <div className="px-4 py-8 text-center text-xs text-gray-600">
        No tasks yet
      </div>
    );
  }

  return (
    <div className="space-y-1 p-2">
      {tasks.map((task) => (
        <button
          key={task.task_id}
          onClick={() => onSelect(task)}
          className={`w-full rounded-lg px-3 py-2.5 text-left transition-colors ${
            task.task_id === activeTaskId
              ? "bg-nexus-600/20 ring-1 ring-nexus-500/30"
              : "hover:bg-gray-800/50"
          }`}
        >
          <div className="flex items-start justify-between gap-2">
            <p className="line-clamp-2 text-xs font-medium text-gray-300">
              {task.query}
            </p>
            <StatusBadge status={task.status} />
          </div>
          <p className="mt-1 text-[10px] text-gray-600">
            {new Date(task.created_at).toLocaleString()}
          </p>
        </button>
      ))}
    </div>
  );
}
