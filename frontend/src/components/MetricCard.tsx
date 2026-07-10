import type { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: string;
  icon?: LucideIcon;
  color?: 'indigo' | 'cyan' | 'emerald' | 'amber' | 'rose';
}

const COLOR_MAP: Record<NonNullable<MetricCardProps['color']>, string> = {
  indigo: 'bg-indigo-500/15 text-indigo-400',
  cyan: 'bg-cyan-500/15 text-cyan-400',
  emerald: 'bg-emerald-500/15 text-emerald-400',
  amber: 'bg-amber-500/15 text-amber-400',
  rose: 'bg-rose-500/15 text-rose-400',
};

export default function MetricCard({
  title,
  value,
  subtitle,
  trend,
  icon: Icon,
  color = 'indigo',
}: MetricCardProps) {
  return (
    <div className="rounded-xl border border-slate-700/60 bg-slate-800 p-5">
      <div className="flex items-start justify-between">
        <div className="min-w-0">
          <p className="text-xs font-medium uppercase tracking-wider text-slate-400">{title}</p>
          <p className="mt-2 truncate text-2xl font-semibold text-white">{value}</p>
          {subtitle && <p className="mt-1 text-xs text-slate-500">{subtitle}</p>}
          {trend && <p className="mt-1 text-xs text-slate-400">{trend}</p>}
        </div>
        {Icon && (
          <div className={`rounded-lg p-2.5 ${COLOR_MAP[color]}`}>
            <Icon size={20} />
          </div>
        )}
      </div>
    </div>
  );
}
