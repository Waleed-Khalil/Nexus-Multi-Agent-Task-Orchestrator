import type { Task } from "../types";

const BASE = "/api/v1";

export async function createTask(query: string): Promise<Task> {
  const res = await fetch(`${BASE}/tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) throw new Error(`Failed to create task: ${res.status}`);
  return res.json();
}

export async function getTask(taskId: string): Promise<Task> {
  const res = await fetch(`${BASE}/tasks/${taskId}`);
  if (!res.ok) throw new Error(`Failed to get task: ${res.status}`);
  return res.json();
}

export async function listTasks(): Promise<Task[]> {
  const res = await fetch(`${BASE}/tasks`);
  if (!res.ok) throw new Error(`Failed to list tasks: ${res.status}`);
  return res.json();
}

export function streamTask(
  taskId: string,
  onEvent: (event: { event: string; data: string }) => void,
  onError: (error: Event) => void,
): EventSource {
  const es = new EventSource(`${BASE}/tasks/${taskId}/stream`);

  const eventTypes = [
    "plan",
    "agent_start",
    "agent_progress",
    "agent_complete",
    "tool_call",
    "tool_result",
    "error",
    "done",
  ];

  for (const type of eventTypes) {
    es.addEventListener(type, (e: MessageEvent) => {
      onEvent({ event: type, data: e.data });
    });
  }

  es.onerror = onError;
  return es;
}
