import { useEffect, useRef } from "react";
import type { StreamEvent } from "../types";
import { AgentIcon } from "./AgentIcon";

interface StreamPanelProps {
  events: StreamEvent[];
  isStreaming: boolean;
}

function formatEventData(event: StreamEvent): string {
  if (event.event === "plan") {
    try {
      const plan = JSON.parse(event.data);
      const lines = [`Plan: ${plan.reasoning}`];
      for (const st of plan.subtasks ?? []) {
        lines.push(`  → [${st.agent}] ${st.description}`);
      }
      return lines.join("\n");
    } catch {
      return event.data;
    }
  }
  if (event.event === "done") {
    return event.data;
  }
  return event.data;
}

const eventStyles: Record<string, string> = {
  plan: "text-nexus-300",
  agent_start: "text-gray-400",
  agent_progress: "text-gray-300",
  agent_complete: "text-emerald-300",
  tool_call: "text-amber-300",
  tool_result: "text-amber-200",
  error: "text-red-400",
  done: "text-emerald-300",
};

export function StreamPanel({ events, isStreaming }: StreamPanelProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events]);

  if (events.length === 0 && !isStreaming) {
    return (
      <div className="flex h-full items-center justify-center rounded-lg border border-gray-800 bg-gray-900/50">
        <div className="text-center">
          <div className="text-4xl">🔮</div>
          <p className="mt-3 text-sm text-gray-500">
            Submit a task to see agent activity here
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col rounded-lg border border-gray-800 bg-gray-900/50">
      <div className="flex items-center justify-between border-b border-gray-800 px-4 py-3">
        <h3 className="text-sm font-semibold text-gray-200">Agent Activity</h3>
        {isStreaming && (
          <span className="flex items-center gap-2 text-xs text-nexus-400">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-nexus-400 opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-nexus-500" />
            </span>
            Live
          </span>
        )}
      </div>

      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 font-mono text-xs leading-relaxed"
      >
        {events.map((event, i) => (
          <div
            key={i}
            className={`mb-2 ${eventStyles[event.event] ?? "text-gray-400"}`}
          >
            <div className="flex items-start gap-2">
              <span className="mt-0.5 shrink-0 text-gray-600">
                {new Date(event.timestamp).toLocaleTimeString()}
              </span>
              {event.agent && (
                <span className="shrink-0">
                  <AgentIcon agent={event.agent} showLabel={false} />
                </span>
              )}
              <span className="whitespace-pre-wrap break-words">
                {event.event === "done" ? (
                  <span className="font-sans text-sm leading-normal text-gray-200">
                    {formatEventData(event)}
                  </span>
                ) : (
                  formatEventData(event)
                )}
              </span>
            </div>
          </div>
        ))}
        {isStreaming && (
          <div className="flex items-center gap-2 text-gray-500">
            <svg className="h-3 w-3 animate-spin" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Agents working...
          </div>
        )}
      </div>
    </div>
  );
}
