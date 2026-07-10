import { useState } from 'react';
import { ChevronDown, FileText } from 'lucide-react';
import type { Citation } from '../api/client';

interface CitationPanelProps {
  citations: Citation[];
}

function CitationCard({ citation, index }: { citation: Citation; index: number }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="rounded-lg border border-slate-700/60 bg-slate-800/60">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center gap-3 px-4 py-3 text-left"
      >
        <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-indigo-500/15 text-xs font-semibold text-indigo-300">
          {index + 1}
        </span>
        <FileText size={15} className="shrink-0 text-slate-500" />
        <span className="min-w-0 flex-1 truncate text-sm font-medium text-slate-200">
          {citation.title}
        </span>
        <span className="shrink-0 rounded-full bg-slate-700/60 px-2 py-0.5 text-xs tabular-nums text-slate-300">
          {(citation.relevance_score * 100).toFixed(1)}% relevant
        </span>
        <ChevronDown
          size={16}
          className={`shrink-0 text-slate-500 transition-transform ${open ? 'rotate-180' : ''}`}
        />
      </button>
      {open && (
        <div className="border-t border-slate-700/60 px-4 py-3">
          <p className="text-xs text-slate-500">Document: {citation.doc_id}</p>
          <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed text-slate-300">
            {citation.chunk_text}
          </p>
        </div>
      )}
    </div>
  );
}

export default function CitationPanel({ citations }: CitationPanelProps) {
  if (citations.length === 0) return null;
  return (
    <div className="space-y-2">
      <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
        Citations ({citations.length})
      </h4>
      {citations.map((c, i) => (
        <CitationCard key={`${c.doc_id}-${i}`} citation={c} index={i} />
      ))}
    </div>
  );
}
