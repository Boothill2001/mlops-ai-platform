import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Zap,
  Layers,
  MessageSquareText,
  Activity,
  ClipboardCheck,
  BookOpen,
} from 'lucide-react';

const NAV_ITEMS = [
  { to: '/', label: 'Overview', icon: LayoutDashboard },
  { to: '/inference', label: 'Online Inference', icon: Zap },
  { to: '/batch', label: 'Batch Jobs', icon: Layers },
  { to: '/rag', label: 'RAG Assistant', icon: MessageSquareText },
  { to: '/monitoring', label: 'Monitoring', icon: Activity },
  { to: '/evaluation', label: 'Evaluation', icon: ClipboardCheck },
  { to: '/tutorial', label: 'Tutorial', icon: BookOpen },
];

export default function Sidebar() {
  return (
    <aside className="flex h-screen w-60 shrink-0 flex-col border-r border-slate-800 bg-slate-950">
      <div className="flex items-center gap-3 px-5 py-6">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-cyan-500 text-sm font-bold text-white">
          CI
        </div>
        <div>
          <div className="text-sm font-semibold text-white">CICAAD Platform</div>
          <div className="text-xs text-slate-500">MLOps AI Dashboard</div>
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-2">
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-indigo-500/15 text-indigo-300'
                  : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
              }`
            }
          >
            <Icon size={18} strokeWidth={2} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-slate-800 px-5 py-4 text-xs text-slate-600">
        Phase 9 — Frontend Dashboard
      </div>
    </aside>
  );
}
