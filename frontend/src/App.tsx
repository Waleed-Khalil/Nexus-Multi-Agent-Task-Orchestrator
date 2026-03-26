import { useCallback, useEffect, useState } from "react";
import type { Task } from "./types";
import { createTask, getTask, listTasks } from "./utils/api";
import { useTaskStream } from "./hooks/useTaskStream";
import { TaskInput } from "./components/TaskInput";
import { StreamPanel } from "./components/StreamPanel";
import { TaskHistory } from "./components/TaskHistory";
import { StatusBadge } from "./components/StatusBadge";
import { AboutPanel } from "./components/AboutPanel";

export default function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [activeTask, setActiveTask] = useState<Task | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const { events, isStreaming, startStream } = useTaskStream();

  // Load task history on mount
  useEffect(() => {
    listTasks().then(setTasks).catch(console.error);
  }, []);

  // Poll active task for final status
  useEffect(() => {
    if (!activeTask || activeTask.status === "complete" || activeTask.status === "failed") return;
    const interval = setInterval(async () => {
      try {
        const updated = await getTask(activeTask.task_id);
        setActiveTask(updated);
        if (updated.status === "complete" || updated.status === "failed") {
          setTasks((prev) =>
            prev.map((t) => (t.task_id === updated.task_id ? updated : t)),
          );
        }
      } catch {
        // ignore
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [activeTask]);

  const handleSubmit = useCallback(
    async (query: string) => {
      setSubmitting(true);
      try {
        const task = await createTask(query);
        setActiveTask(task);
        setTasks((prev) => [task, ...prev]);
        startStream(task.task_id);
      } catch (err) {
        console.error("Failed to create task:", err);
      } finally {
        setSubmitting(false);
      }
    },
    [startStream],
  );

  const handleSelectTask = useCallback(
    (task: Task) => {
      setActiveTask(task);
      if (task.status === "running" || task.status === "pending") {
        startStream(task.task_id);
      }
    },
    [startStream],
  );

  return (
    <div className="flex h-screen flex-col">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-gray-800 bg-gray-950/80 px-6 py-4 backdrop-blur">
        <div className="flex items-center gap-3">
          <img src="/nexus.svg" alt="Nexus" className="h-8 w-8" />
          <div>
            <h1 className="text-lg font-bold tracking-tight text-white">
              Nexus
            </h1>
            <p className="text-[11px] text-gray-500">
              Multi-Agent Task Orchestrator
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <AboutPanel />
          {activeTask && (
            <>
              <StatusBadge status={activeTask.status} />
              <span className="max-w-xs truncate text-xs text-gray-500">
                {activeTask.task_id.slice(0, 8)}...
              </span>
            </>
          )}
        </div>
      </header>

      {/* Main Content */}
      <div className="flex min-h-0 flex-1">
        {/* Sidebar */}
        <aside className="flex w-72 flex-col border-r border-gray-800 bg-gray-950/50">
          <div className="border-b border-gray-800 px-4 py-3">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
              Task History
            </h2>
          </div>
          <div className="flex-1 overflow-y-auto">
            <TaskHistory
              tasks={tasks}
              activeTaskId={activeTask?.task_id ?? null}
              onSelect={handleSelectTask}
            />
          </div>
        </aside>

        {/* Center */}
        <main className="flex flex-1 flex-col">
          {/* Task Input */}
          <div className="border-b border-gray-800 bg-gray-900/30 px-6 py-5">
            <TaskInput onSubmit={handleSubmit} disabled={submitting || isStreaming} />
          </div>

          {/* Stream Panel */}
          <div className="min-h-0 flex-1 p-4">
            <StreamPanel events={events} isStreaming={isStreaming} />
          </div>

          {/* Final Answer */}
          {activeTask?.final_answer && (
            <div className="border-t border-gray-800 bg-gray-900/50 px-6 py-5">
              <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-emerald-400">
                Final Answer
              </h3>
              <div className="prose prose-invert prose-sm max-w-none whitespace-pre-wrap text-sm leading-relaxed text-gray-300">
                {activeTask.final_answer}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
