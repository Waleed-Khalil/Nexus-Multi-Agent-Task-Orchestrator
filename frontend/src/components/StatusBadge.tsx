import type { TaskStatus } from "../types";

const config: Record<TaskStatus, { label: string; classes: string }> = {
  pending: {
    label: "Pending",
    classes: "bg-gray-700/50 text-gray-300 ring-gray-600",
  },
  running: {
    label: "Running",
    classes: "bg-nexus-600/20 text-nexus-300 ring-nexus-500 animate-pulse",
  },
  complete: {
    label: "Complete",
    classes: "bg-emerald-600/20 text-emerald-300 ring-emerald-500",
  },
  failed: {
    label: "Failed",
    classes: "bg-red-600/20 text-red-300 ring-red-500",
  },
};

export function StatusBadge({ status }: { status: TaskStatus }) {
  const { label, classes } = config[status];
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${classes}`}
    >
      {label}
    </span>
  );
}
