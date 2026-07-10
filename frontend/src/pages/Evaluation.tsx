import { useEffect, useState } from 'react';
import { AlertOctagon, CheckCircle2, FlaskConical, Loader2 } from 'lucide-react';
import MetricCard from '../components/MetricCard';
import DataTable, { ColumnDef } from '../components/DataTable';
import {
  runEvaluation,
  getGoldenQuestions,
  EvaluationResult,
  FailedCase,
  GoldenQuestion,
} from '../api/client';

export default function Evaluation() {
  const [result, setResult] = useState<EvaluationResult | null>(null);
  const [questions, setQuestions] = useState<GoldenQuestion[]>([]);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getGoldenQuestions().then(setQuestions).catch(() => {});
  }, []);

  const run = async () => {
    setRunning(true);
    setError(null);
    try {
      setResult(await runEvaluation({ top_k: 5, role: 'analyst' }));
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Evaluation failed');
    } finally {
      setRunning(false);
    }
  };

  const pct = (v: number) => `${(v * 100).toFixed(1)}%`;

  const failedColumns: ColumnDef<FailedCase>[] = [
    {
      header: 'Question',
      cell: (r) => <span className="text-slate-200">{r.question}</span>,
    },
    { header: 'Recall', cell: (r) => pct(r.recall) },
    {
      header: 'Expected Docs',
      cell: (r) => <span className="font-mono text-xs">{r.expected_docs.join(', ')}</span>,
    },
    {
      header: 'Retrieved Docs',
      cell: (r) => <span className="font-mono text-xs">{r.retrieved_docs.join(', ') || '—'}</span>,
    },
  ];

  return (
    <div className="space-y-6 p-8">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-white">Evaluation</h1>
          <p className="mt-1 text-sm text-slate-400">
            RAG quality gates against {questions.length || '…'} golden questions — recall@k,
            precision@k, faithfulness, citation accuracy
          </p>
        </div>
        <button
          onClick={run}
          disabled={running}
          className="flex items-center gap-2 rounded-lg bg-indigo-500 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {running ? <Loader2 size={15} className="animate-spin" /> : <FlaskConical size={15} />}
          {running ? 'Running…' : 'Run Evaluation'}
        </button>
      </div>

      {error && (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {result && (
        <>
          {result.regression_detected ? (
            <div className="flex items-center gap-3 rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-3">
              <AlertOctagon size={18} className="shrink-0 text-red-400" />
              <div>
                <div className="text-sm font-semibold text-red-300">Regression detected</div>
                <div className="text-xs text-red-400/80">
                  Aggregate quality dropped below release thresholds — this build should not ship.
                </div>
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-3 rounded-lg border border-emerald-500/40 bg-emerald-500/10 px-4 py-3">
              <CheckCircle2 size={18} className="shrink-0 text-emerald-400" />
              <div>
                <div className="text-sm font-semibold text-emerald-300">Quality gate passed</div>
                <div className="text-xs text-emerald-400/80">
                  {result.passed_questions}/{result.total_questions} questions passed retrieval
                  thresholds.
                </div>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <MetricCard title="Recall@k" value={pct(result.recall_at_k)} color="indigo" />
            <MetricCard title="Precision@k" value={pct(result.precision_at_k)} color="cyan" />
            <MetricCard title="Faithfulness" value={pct(result.faithfulness)} color="emerald" />
            <MetricCard
              title="Citation Accuracy"
              value={pct(result.citation_accuracy)}
              color="amber"
            />
          </div>

          <div>
            <h3 className="mb-3 text-sm font-semibold text-white">
              Failed Cases ({result.failed_cases.length})
            </h3>
            <DataTable
              columns={failedColumns}
              data={result.failed_cases}
              rowKey={(r) => r.question}
              emptyMessage="No failed cases — all questions met the recall threshold"
            />
          </div>
        </>
      )}

      {!result && !running && (
        <div className="rounded-xl border border-dashed border-slate-700 py-16 text-center text-sm text-slate-500">
          Run the evaluation to score the RAG pipeline against the golden dataset.
        </div>
      )}

      <div>
        <h3 className="mb-3 text-sm font-semibold text-white">Golden Questions</h3>
        <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
          {questions.map((q, i) => (
            <div
              key={i}
              className="rounded-lg border border-slate-700/60 bg-slate-800/60 px-4 py-3"
            >
              <div className="text-sm text-slate-200">{q.question}</div>
              {Array.isArray(q.expected_doc_ids) && (
                <div className="mt-1 font-mono text-xs text-slate-500">
                  expects: {(q.expected_doc_ids as string[]).join(', ')}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
