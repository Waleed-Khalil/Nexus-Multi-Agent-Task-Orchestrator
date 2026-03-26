export type AgentType = "orchestrator" | "research" | "code_gen" | "data_analysis";
export type TaskStatus = "pending" | "running" | "complete" | "failed";
export type StreamEventType =
  | "plan"
  | "agent_start"
  | "agent_progress"
  | "agent_complete"
  | "tool_call"
  | "tool_result"
  | "error"
  | "done";

export interface SubTask {
  id: string;
  agent: AgentType;
  description: string;
  dependencies: string[];
  status: TaskStatus;
}

export interface SubTaskResult {
  subtask_id: string;
  agent: AgentType;
  status: TaskStatus;
  result: string;
  error: string | null;
  duration_ms: number;
}

export interface Task {
  task_id: string;
  status: TaskStatus;
  query: string;
  plan: SubTask[];
  results: SubTaskResult[];
  final_answer: string | null;
  created_at: string;
  completed_at: string | null;
}

export interface StreamEvent {
  event: StreamEventType;
  agent: AgentType | null;
  data: string;
  subtask_id: string | null;
  timestamp: string;
}
