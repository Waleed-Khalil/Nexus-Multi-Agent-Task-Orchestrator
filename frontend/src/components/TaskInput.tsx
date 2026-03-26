import { useState } from "react";

const examples = [
  {
    label: "Research + Code",
    prompt:
      "Research the top 3 sorting algorithms by time complexity, then write optimized Python implementations of each with benchmarks.",
  },
  {
    label: "Data Analysis",
    prompt:
      "Analyze quarterly revenue data: Q1 $1.2M, Q2 $1.8M, Q3 $1.4M, Q4 $2.3M. Identify trends, detect anomalies, and suggest forecasting approaches.",
  },
  {
    label: "Full Pipeline",
    prompt:
      "Research best practices for building REST APIs, then generate a FastAPI CRUD application for a todo list with proper error handling, and analyze the performance characteristics of different database choices.",
  },
  {
    label: "Code Review",
    prompt:
      "Write a Python binary search tree implementation with insert, delete, and search operations. Include type hints and validate the code for correctness.",
  },
];

interface TaskInputProps {
  onSubmit: (query: string) => void;
  disabled: boolean;
}

export function TaskInput({ onSubmit, disabled }: TaskInputProps) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = query.trim();
    if (!trimmed || disabled) return;
    onSubmit(trimmed);
    setQuery("");
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <label
        htmlFor="task-input"
        className="block text-sm font-medium text-gray-300"
      >
        Describe your task
      </label>
      <textarea
        id="task-input"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="e.g. Research the latest trends in AI agents, then write a Python script that demonstrates a simple multi-agent system..."
        rows={4}
        disabled={disabled}
        className="w-full rounded-lg border border-gray-700 bg-gray-800/50 px-4 py-3 text-sm text-gray-100 placeholder-gray-500 shadow-sm backdrop-blur transition-colors focus:border-nexus-500 focus:outline-none focus:ring-1 focus:ring-nexus-500 disabled:opacity-50"
        onKeyDown={(e) => {
          if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
            handleSubmit(e);
          }
        }}
      />
      {!query && !disabled && (
        <div className="flex flex-wrap gap-2">
          <span className="self-center text-[11px] text-gray-600">Try:</span>
          {examples.map((ex) => (
            <button
              key={ex.label}
              type="button"
              onClick={() => setQuery(ex.prompt)}
              className="rounded-full border border-gray-700/60 bg-gray-800/40 px-3 py-1 text-[11px] font-medium text-gray-400 transition-colors hover:border-nexus-500/40 hover:bg-nexus-600/10 hover:text-nexus-300"
            >
              {ex.label}
            </button>
          ))}
        </div>
      )}

      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-500">
          {navigator.platform.includes("Mac") ? "⌘" : "Ctrl"}+Enter to submit
        </span>
        <button
          type="submit"
          disabled={disabled || !query.trim()}
          className="inline-flex items-center gap-2 rounded-lg bg-nexus-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition-all hover:bg-nexus-500 focus:outline-none focus:ring-2 focus:ring-nexus-500 focus:ring-offset-2 focus:ring-offset-gray-950 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {disabled ? (
            <>
              <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Processing...
            </>
          ) : (
            <>
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Execute Task
            </>
          )}
        </button>
      </div>
    </form>
  );
}
