import { useCallback, useEffect, useRef, useState } from 'react';
import { Play, RefreshCw, X } from 'lucide-react';
import DataTable, { ColumnDef } from '../components/DataTable';
import ProgressBar from '../components/ProgressBar';
import StatusBadge from '../components/StatusBadge';
import { getBatchJob, getBatchJobs, runSampleBatch, BatchJob, BatchJobResult } from '../api/client';

const POLL_INTERVAL_MS = 2000;

function isActive(job: BatchJob): boolean {
  const s = job.status.toLowerCase();
  return s === 'pending' || s === 'running';
}

export default function BatchJobs() {
  const [jobs, setJobs] = useState<BatchJob[]>([]);
  const [selected, setSelected] = useState<BatchJob | null>(null);
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const selectedIdRef = useRef<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const list = await getBatchJobs();
      setJobs(list);
      setError(null);
      if (selectedIdRef.current) {
        const detail = await getBatchJob(selectedIdRef.current);
        setSelected(detail);
      }
      return list;
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load jobs');
      return [];
    }
  }, []);

  // Initial load + poll every 2s while any job is active.
  useEffect(() => {
    let timer: ReturnType<typeof setInterval> | null = null;
    refresh();
    timer = setInterval(async () => {
      const list = await refresh();
      if (timer && list.length > 0 && !list.some(isActive)) {
        // keep polling only while something is running; restart handled by deps below
      }
    }, POLL_INTERVAL_MS);
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [refresh]);

  async function handleRunSample() {
    setStarting(true);
    setError(null);
    try {
      await runSampleBatch();
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to start batch job');
    } finally {
      setStarting(false);
    }
  }

  async function handleSelect(job: BatchJob) {
    selectedIdRef.current = job.job_id;
    try {
      setSelected(await getBatchJob(job.job_id));
    } catch {
      setSelected(job);
    }
  }

  function clearSelection() {
    selectedIdRef.current = null;
    setSelected(null);
  }

  const jobColumns: ColumnDef<BatchJob>[] = [
    {
      header: 'Job ID',
      cell: (j) => <span className="font-mono text-xs text-slate-300">{j.job_id}</span>,
    },
    { header: 'Status', cell: (j) => <StatusBadge status={j.status} /> },
    {
      header: 'Progress',
      cell: (j) => (
        <div className="min-w-[160px]">
          <ProgressBar value={j.progress_pct} />
        </div>
      ),
    },
    {
      header: 'Records',
      cell: (j) => (
        <span className="tabular-nums">
          {j.processed_records}/{j.total_records}
          {j.failed_records > 0 && (
            <span className="ml-1 text-red-400">({j.failed_records} failed)</span>
          )}
        </span>
      ),
    },
    {
      header: 'Created',
      cell: (j) => <span className="text-xs text-slate-400">{new Date(j.created_at).toLocaleString()}</span>,
    },
    {
      header: 'Completed',
      cell: (j) => (
        <span className="text-xs text-slate-400">
          {j.completed_at ? new Date(j.completed_at).toLocaleString() : '—'}
        </span>
      ),
    },
  ];

  const resultColumns: ColumnDef<BatchJobResult>[] = [
    {
      header: 'Supplier',
      cell: (r) => <span className="font-mono text-xs">{String(r.supplier_id ?? '—')}</span>,
    },
    {
      header: 'Risk Score',
      cell: (r) =>
        typeof r.risk_score === 'number' ? (
          <span className="tabular-nums">{r.risk_score.toFixed(4)}</span>
        ) : (
          '—'
        ),
    },
    {
      header: 'Risk Level',
      cell: (r) => (r.risk_level ? <StatusBadge status={String(r.risk_level)} /> : '—'),
    },
  ];

  const anyRunning = jobs.some(isActive);

  return (
    <div className="space-y-6 p-8">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-white">Batch Jobs</h1>
          <p className="mt-1 text-sm text-slate-400">
            Chunked batch scoring with progress tracking
            {anyRunning && ' · auto-refreshing every 2s'}
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => refresh()}
            className="flex items-center gap-2 rounded-lg border border-slate-600 px-4 py-2 text-sm font-medium text-slate-300 transition-colors hover:bg-slate-800"
          >
            <RefreshCw size={15} />
            Refresh
          </button>
          <button
            onClick={handleRunSample}
            disabled={starting}
            className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Play size={15} />
            {starting ? 'Starting…' : 'Run Sample Batch'}
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      <DataTable
        columns={jobColumns}
        data={jobs}
        rowKey={(j) => j.job_id}
        onRowClick={handleSelect}
        emptyMessage="No batch jobs yet — run a sample batch to get started"
      />

      {selected && (
        <div className="rounded-xl border border-slate-700/60 bg-slate-800 p-6">
          <div className="mb-4 flex items-start justify-between">
            <div>
              <h3 className="text-sm font-semibold text-white">
                Job Detail — <span className="font-mono text-xs">{selected.job_id}</span>
              </h3>
              <div className="mt-2 flex items-center gap-4 text-xs text-slate-400">
                <StatusBadge status={selected.status} />
                <span className="tabular-nums">
                  {selected.processed_records}/{selected.total_records} processed
                </span>
                {selected.failed_records > 0 && (
                  <span className="text-red-400">{selected.failed_records} failed</span>
                )}
              </div>
            </div>
            <button
              onClick={clearSelection}
              className="rounded-lg p-1.5 text-slate-500 transition-colors hover:bg-slate-700 hover:text-slate-300"
              aria-label="Close job detail"
            >
              <X size={16} />
            </button>
          </div>
          <div className="mb-5">
            <ProgressBar value={selected.progress_pct} />
          </div>
          {selected.results && selected.results.length > 0 ? (
            <DataTable
              columns={resultColumns}
              data={selected.results}
              rowKey={(r, i) => `${r.supplier_id ?? 'row'}-${i}`}
            />
          ) : (
            <p className="text-sm text-slate-500">No results yet.</p>
          )}
        </div>
      )}
    </div>
  );
}
