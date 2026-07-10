import { useState } from 'react';
import { Loader2, Lock, Search, Send } from 'lucide-react';
import CitationPanel from '../components/CitationPanel';
import { ragQuery, RagQueryResponse } from '../api/client';

const ROLES = ['admin', 'manager', 'analyst', 'viewer'] as const;

const SAMPLE_QUERIES = [
  'What are the quality issues with our steel suppliers?',
  'Summarize the latest compliance audit findings',
  'What is the pricing forecast for raw materials?',
];

export default function RagAssistant() {
  const [role, setRole] = useState<string>('analyst');
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<RagQueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (q?: string) => {
    const text = (q ?? query).trim();
    if (!text || loading) return;
    setLoading(true);
    setError(null);
    setQuery(text);
    try {
      const res = await ragQuery({ user_id: 'dashboard_user', role, query: text, top_k: 5 });
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Query failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 p-8">
      <div>
        <h1 className="text-2xl font-semibold text-white">RAG Assistant</h1>
        <p className="mt-1 text-sm text-slate-400">
          Permission-aware retrieval — documents are filtered by role before ranking
        </p>
      </div>

      <div className="rounded-xl border border-slate-700/60 bg-slate-800 p-5">
        <div className="flex flex-col gap-3 sm:flex-row">
          <div className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-900 px-3">
            <Lock size={14} className="text-slate-500" />
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="bg-transparent py-2.5 text-sm capitalize text-slate-200 outline-none"
            >
              {ROLES.map((r) => (
                <option key={r} value={r} className="bg-slate-900 capitalize">
                  {r}
                </option>
              ))}
            </select>
          </div>
          <div className="flex flex-1 items-center gap-2 rounded-lg border border-slate-700 bg-slate-900 px-3">
            <Search size={15} className="shrink-0 text-slate-500" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && submit()}
              placeholder="Ask about suppliers, quality, compliance, pricing…"
              className="w-full bg-transparent py-2.5 text-sm text-slate-200 placeholder-slate-600 outline-none"
            />
          </div>
          <button
            onClick={() => submit()}
            disabled={loading || !query.trim()}
            className="flex items-center justify-center gap-2 rounded-lg bg-indigo-500 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-40"
          >
            {loading ? <Loader2 size={15} className="animate-spin" /> : <Send size={15} />}
            Ask
          </button>
        </div>

        <div className="mt-3 flex flex-wrap gap-2">
          {SAMPLE_QUERIES.map((q) => (
            <button
              key={q}
              onClick={() => submit(q)}
              disabled={loading}
              className="rounded-full border border-slate-700 bg-slate-800/80 px-3 py-1 text-xs text-slate-400 transition hover:border-indigo-500/50 hover:text-indigo-300 disabled:opacity-40"
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {result && (
        <>
          <div className="rounded-xl border border-slate-700/60 bg-slate-800 p-6">
            <div className="mb-4 flex flex-wrap items-center gap-2 text-xs">
              <span className="rounded-full bg-slate-700/60 px-2.5 py-1 tabular-nums text-slate-300">
                {result.latency_ms.toFixed(1)} ms
              </span>
              <span
                className={`rounded-full px-2.5 py-1 ${
                  result.cache_hit
                    ? 'bg-emerald-500/15 text-emerald-400'
                    : 'bg-slate-700/60 text-slate-400'
                }`}
              >
                {result.cache_hit ? 'cache hit' : 'cache miss'}
              </span>
              <span className="rounded-full bg-slate-700/60 px-2.5 py-1 text-slate-300">
                {result.chunks_retrieved} chunks retrieved
              </span>
              <span className="rounded-full bg-amber-500/15 px-2.5 py-1 text-amber-400">
                {result.permission_filtered_count} filtered by permissions
              </span>
              {result.grounded && (
                <span className="rounded-full bg-indigo-500/15 px-2.5 py-1 text-indigo-300">
                  grounded
                </span>
              )}
            </div>
            <div className="whitespace-pre-wrap text-sm leading-relaxed text-slate-200">
              {result.answer}
            </div>
          </div>

          {result.citations.length > 0 && (
            <div>
              <h3 className="mb-3 text-sm font-semibold text-white">
                Citations ({result.citations.length})
              </h3>
              <CitationPanel citations={result.citations} />
            </div>
          )}
        </>
      )}

      {!result && !loading && !error && (
        <div className="rounded-xl border border-dashed border-slate-700 py-16 text-center text-sm text-slate-500">
          Ask a question to search the document base. Try switching roles to see permission
          filtering in action — a viewer sees fewer documents than an admin.
        </div>
      )}
    </div>
  );
}
