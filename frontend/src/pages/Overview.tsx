import { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';
import { Activity, DollarSign, Gauge, Server } from 'lucide-react';
import MetricCard from '../components/MetricCard';
import ChartContainer from '../components/ChartContainer';
import {
  getMonitoringMetrics,
  getMonitoringHistory,
  MonitoringMetrics,
  HistoryRecord,
} from '../api/client';
import { CATEGORICAL, CHART_GRID, CHART_TEXT, STATUS, TOOLTIP_STYLE } from '../theme';

export default function Overview() {
  const [metrics, setMetrics] = useState<MonitoringMetrics | null>(null);
  const [history, setHistory] = useState<HistoryRecord[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getMonitoringMetrics(), getMonitoringHistory()])
      .then(([m, h]) => {
        setMetrics(m);
        setHistory(h);
      })
      .catch((e) => setError(e?.message ?? 'Failed to load metrics'));
  }, []);

  const latencySeries = history.slice(-50).map((r, i) => ({
    index: i + 1,
    latency: r.latency_ms ?? 0,
    endpoint: r.endpoint ?? '',
  }));

  const endpointDist = (metrics?.per_endpoint ?? []).map((e) => ({
    name: e.endpoint,
    value: e.count,
  }));

  const driftOk = metrics?.drift?.drift_status?.toLowerCase() === 'stable'
    || metrics?.drift?.drift_status?.toLowerCase() === 'ok'
    || metrics?.drift?.drift_status?.toLowerCase() === 'no_drift';

  return (
    <div className="space-y-6 p-8">
      <div>
        <h1 className="text-2xl font-semibold text-white">Platform Overview</h1>
        <p className="mt-1 text-sm text-slate-400">
          Live health snapshot of inference, RAG, and batch workloads
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          {error} — is the backend running at localhost:8000?
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          title="Total Requests"
          value={metrics ? metrics.total_requests.toLocaleString() : '—'}
          subtitle={`${metrics?.requests_per_minute?.toFixed(1) ?? '—'} req/min`}
          icon={Server}
          color="indigo"
        />
        <MetricCard
          title="Latency p50"
          value={metrics ? `${metrics.latency_p50.toFixed(1)} ms` : '—'}
          subtitle={`p95: ${metrics?.latency_p95?.toFixed(1) ?? '—'} ms`}
          icon={Gauge}
          color="cyan"
        />
        <MetricCard
          title="Cache Hit Rate"
          value={metrics ? `${(metrics.cache_hit_rate * 100).toFixed(1)}%` : '—'}
          subtitle={`Error rate: ${((metrics?.error_rate ?? 0) * 100).toFixed(2)}%`}
          icon={Activity}
          color="emerald"
        />
        <MetricCard
          title="Estimated Cost"
          value={metrics ? `$${metrics.estimated_cost.toFixed(4)}` : '—'}
          subtitle={`Citation rate: ${((metrics?.rag_citation_rate ?? 0) * 100).toFixed(0)}%`}
          icon={DollarSign}
          color="amber"
        />
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <div className="xl:col-span-2">
          <ChartContainer title="Request Latency" subtitle="Most recent requests (ms)">
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={latencySeries} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
                <CartesianGrid stroke={CHART_GRID} strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="index" stroke={CHART_TEXT} fontSize={11} tickLine={false} />
                <YAxis stroke={CHART_TEXT} fontSize={11} tickLine={false} axisLine={false} unit=" ms" />
                <Tooltip
                  contentStyle={TOOLTIP_STYLE}
                  formatter={(v: number) => [`${v.toFixed(1)} ms`, 'Latency']}
                  labelFormatter={(l) => `Request #${l}`}
                />
                <Line
                  type="monotone"
                  dataKey="latency"
                  stroke={CATEGORICAL[0]}
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </ChartContainer>
        </div>

        <ChartContainer title="Requests by Endpoint" subtitle="Distribution across API surface">
          {endpointDist.length === 0 ? (
            <p className="py-20 text-center text-sm text-slate-500">No endpoint data yet</p>
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={endpointDist}
                  dataKey="value"
                  nameKey="name"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={2}
                  stroke="#1e293b"
                  strokeWidth={2}
                >
                  {endpointDist.map((_, i) => (
                    <Cell key={i} fill={CATEGORICAL[i % CATEGORICAL.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={TOOLTIP_STYLE} />
                <Legend
                  wrapperStyle={{ fontSize: 11, color: CHART_TEXT }}
                  iconType="circle"
                  iconSize={8}
                />
              </PieChart>
            </ResponsiveContainer>
          )}
        </ChartContainer>
      </div>

      <div className="rounded-xl border border-slate-700/60 bg-slate-800 p-5">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white">Data Drift Status</h3>
            <p className="mt-0.5 text-xs text-slate-500">
              Population Stability Index on supplier risk features
              {metrics?.drift ? ` · sample size ${metrics.drift.sample_size}` : ''}
            </p>
          </div>
          {metrics?.drift && (
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-xs text-slate-500">Drift score</div>
                <div className="text-lg font-semibold tabular-nums text-white">
                  {metrics.drift.drift_score.toFixed(4)}
                </div>
              </div>
              <span
                className="inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-sm font-medium capitalize"
                style={{
                  color: driftOk ? STATUS.good : STATUS.serious,
                  borderColor: driftOk ? `${STATUS.good}55` : `${STATUS.serious}55`,
                  backgroundColor: driftOk ? `${STATUS.good}1a` : `${STATUS.serious}1a`,
                }}
              >
                <span
                  className="h-2 w-2 rounded-full"
                  style={{ backgroundColor: driftOk ? STATUS.good : STATUS.serious }}
                />
                {metrics.drift.drift_status.replace(/_/g, ' ')}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
