import { useEffect, useState } from "react";
import { createPortal } from "react-dom";

const agents = [
  {
    icon: "🔍",
    name: "Research Agent",
    color: "text-amber-400",
    border: "border-amber-500/30",
    bg: "bg-amber-500/5",
    description:
      "Investigates topics using web search, document summarization, and fact-checking. Returns structured findings with confidence scores.",
    tools: ["web_search", "summarize_document", "fact_check"],
  },
  {
    icon: "💻",
    name: "Code Gen Agent",
    color: "text-emerald-400",
    border: "border-emerald-500/30",
    bg: "bg-emerald-500/5",
    description:
      "Writes production-quality code, validates syntax, generates test stubs, and explains existing code line-by-line.",
    tools: ["validate_python", "generate_tests", "explain_code"],
  },
  {
    icon: "📊",
    name: "Data Analysis Agent",
    color: "text-violet-400",
    border: "border-violet-500/30",
    bg: "bg-violet-500/5",
    description:
      "Performs statistical analysis, detects outliers using z-score methods, and recommends appropriate visualizations.",
    tools: ["compute_statistics", "detect_outliers", "suggest_visualization"],
  },
];

const steps = [
  {
    num: "1",
    title: "You describe a complex task",
    detail:
      "Write a natural-language request — it can span research, coding, and data analysis all at once.",
  },
  {
    num: "2",
    title: "Orchestrator plans the work",
    detail:
      "Claude decomposes your request into an ordered set of subtasks and assigns each to the best specialist agent.",
  },
  {
    num: "3",
    title: "Agents execute with tools",
    detail:
      "Each agent runs autonomously — calling its own tools, retrying on validation errors (up to 3x), and streaming progress in real time.",
  },
  {
    num: "4",
    title: "Results are synthesized",
    detail:
      "The orchestrator combines all agent outputs into a single cohesive answer delivered back to you.",
  },
];

function Modal({ onClose }: { onClose: () => void }) {
  // Lock body scroll while modal is open
  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
    };
  }, []);

  return (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center p-4"
      style={{ isolation: "isolate" }}
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Dialog */}
      <div className="relative z-10 flex max-h-[85vh] w-full max-w-3xl flex-col rounded-2xl border border-gray-800 bg-gray-950 shadow-2xl">
        {/* Sticky header with close button */}
        <div className="flex items-center justify-between border-b border-gray-800 px-8 py-4">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🔮</span>
            <h2 className="text-lg font-bold tracking-tight text-white">
              About Nexus
            </h2>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-gray-500 transition-colors hover:bg-gray-800 hover:text-gray-300"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Scrollable content */}
        <div className="overflow-y-auto p-8">
          <p className="mb-8 text-center text-sm leading-relaxed text-gray-400">
            A multi-agent task orchestration system that breaks down complex requests
            and delegates them to specialized AI agents — each with their own tools,
            expertise, and validation logic.
          </p>

          {/* Architecture diagram */}
          <div className="mb-8 rounded-xl border border-gray-800 bg-gray-900/50 p-5">
            <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-500">
              Architecture
            </h3>
            <pre className="overflow-x-auto font-mono text-[11px] leading-relaxed text-gray-400">
{`                     ┌─────────────────────┐
                     │    Your Request     │
                     └──────────┬──────────┘
                                │
                     ┌──────────▼──────────┐
                     │    Orchestrator     │
                     │  Decomposes & Plans │
                     └───┬───────┬──────┬──┘
                         │       │      │
            ┌────────────┘       │      └────────────┐
            │                    │                    │
   ┌────────▼────────┐ ┌────────▼───────┐ ┌─────────▼────────┐
   │ Research Agent  │ │ CodeGen Agent  │ │ DataAnalysis     │
   │                 │ │                │ │ Agent            │
   │ web_search      │ │ validate_py    │ │ statistics       │
   │ summarize       │ │ gen_tests      │ │ outliers         │
   │ fact_check      │ │ explain_code   │ │ visualizations   │
   └────────┬────────┘ └────────┬───────┘ └─────────┬────────┘
            │                    │                    │
            └────────────┐       │      ┌─────────────┘
                         │       │      │
                     ┌───▼───────▼──────▼──┐
                     │    Synthesizer      │
                     │  Combines results   │
                     └─────────────────────┘`}
            </pre>
          </div>

          {/* How it works */}
          <div className="mb-8">
            <h3 className="mb-4 text-xs font-semibold uppercase tracking-wider text-gray-500">
              How it works
            </h3>
            <div className="grid gap-3 sm:grid-cols-2">
              {steps.map((step) => (
                <div
                  key={step.num}
                  className="rounded-xl border border-gray-800 bg-gray-900/30 p-4"
                >
                  <div className="mb-2 flex items-center gap-2.5">
                    <span className="flex h-6 w-6 items-center justify-center rounded-full bg-nexus-600/20 text-xs font-bold text-nexus-400 ring-1 ring-nexus-500/30">
                      {step.num}
                    </span>
                    <span className="text-sm font-semibold text-gray-200">
                      {step.title}
                    </span>
                  </div>
                  <p className="pl-[34px] text-xs leading-relaxed text-gray-500">
                    {step.detail}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Agent cards */}
          <div className="mb-8">
            <h3 className="mb-4 text-xs font-semibold uppercase tracking-wider text-gray-500">
              Specialist Agents
            </h3>
            <div className="grid gap-3 sm:grid-cols-3">
              {agents.map((agent) => (
                <div
                  key={agent.name}
                  className={`rounded-xl border ${agent.border} ${agent.bg} p-4`}
                >
                  <div className="mb-2 flex items-center gap-2">
                    <span className="text-lg">{agent.icon}</span>
                    <span className={`text-sm font-semibold ${agent.color}`}>
                      {agent.name}
                    </span>
                  </div>
                  <p className="mb-3 text-xs leading-relaxed text-gray-400">
                    {agent.description}
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {agent.tools.map((tool) => (
                      <span
                        key={tool}
                        className="rounded-md bg-gray-800/80 px-2 py-0.5 font-mono text-[10px] text-gray-500"
                      >
                        {tool}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Tech stack */}
          <div className="rounded-xl border border-gray-800 bg-gray-900/30 p-5">
            <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-500">
              Tech Stack
            </h3>
            <div className="grid grid-cols-2 gap-x-8 gap-y-2 text-xs sm:grid-cols-4">
              {[
                { label: "Backend", value: "FastAPI + Python" },
                { label: "AI", value: "Claude API" },
                { label: "Orchestration", value: "LangGraph" },
                { label: "Validation", value: "Pydantic v2" },
                { label: "Frontend", value: "React + TypeScript" },
                { label: "Styling", value: "Tailwind CSS" },
                { label: "Streaming", value: "SSE" },
                { label: "Infra", value: "Docker" },
              ].map((item) => (
                <div key={item.label}>
                  <span className="text-gray-600">{item.label}: </span>
                  <span className="font-medium text-gray-300">
                    {item.value}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export function AboutPanel() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="rounded-lg border border-gray-700 px-3 py-1.5 text-xs font-medium text-gray-400 transition-colors hover:border-gray-600 hover:text-gray-200"
      >
        How it works
      </button>

      {open && createPortal(
        <Modal onClose={() => setOpen(false)} />,
        document.body,
      )}
    </>
  );
}
