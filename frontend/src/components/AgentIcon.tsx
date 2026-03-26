import type { AgentType } from "../types";

const agentMeta: Record<
  AgentType,
  { icon: string; label: string; color: string }
> = {
  orchestrator: { icon: "🎯", label: "Orchestrator", color: "text-nexus-400" },
  research: { icon: "🔍", label: "Research", color: "text-amber-400" },
  code_gen: { icon: "💻", label: "Code Gen", color: "text-emerald-400" },
  data_analysis: { icon: "📊", label: "Data Analysis", color: "text-violet-400" },
};

export function AgentIcon({
  agent,
  showLabel = true,
}: {
  agent: AgentType;
  showLabel?: boolean;
}) {
  const meta = agentMeta[agent];
  return (
    <span className={`inline-flex items-center gap-1.5 ${meta.color}`}>
      <span className="text-sm">{meta.icon}</span>
      {showLabel && (
        <span className="text-xs font-medium">{meta.label}</span>
      )}
    </span>
  );
}
