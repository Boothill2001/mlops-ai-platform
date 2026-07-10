interface StatusBadgeProps {
  status: string;
}

// Colored pill for risk levels and job statuses.
// Never color-alone: the label text is always shown.
const STYLES: Record<string, string> = {
  // risk levels
  low: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
  medium: 'bg-yellow-500/15 text-yellow-400 border-yellow-500/30',
  high: 'bg-orange-500/15 text-orange-400 border-orange-500/30',
  critical: 'bg-red-500/15 text-red-400 border-red-500/30',
  // job statuses
  pending: 'bg-slate-500/15 text-slate-400 border-slate-500/30',
  running: 'bg-cyan-500/15 text-cyan-400 border-cyan-500/30',
  completed: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
  failed: 'bg-red-500/15 text-red-400 border-red-500/30',
};

const FALLBACK = 'bg-slate-500/15 text-slate-400 border-slate-500/30';

export default function StatusBadge({ status }: StatusBadgeProps) {
  const key = status?.toLowerCase() ?? '';
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium capitalize ${
        STYLES[key] ?? FALLBACK
      }`}
    >
      {status}
    </span>
  );
}
