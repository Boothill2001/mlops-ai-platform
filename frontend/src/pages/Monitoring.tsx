import { useCallback, useEffect, useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { AlertTriangle, Clock, Percent, RefreshCw, Zap } from 'lucide-react';
import MetricCard from '../components/MetricCard';
import ChartContainer from '../components/ChartContainer';
import DataTable, { ColumnDef } from '../components/DataTable';
import { getMonitoringMetrics, MonitoringMetrics, EndpointMetric } from '../api/client';
import { CATEGORICAL, CHART_GRID, CHART_TEXT, SERIES, STATUS, TOOLTIP_STYLE } from '../theme';

export default function Monitoring() {
  const [metrics, setMetrics] = useState<MonitoringMetrics | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(() => {
    setRefreshing(true);
    getMonitoringMetrics()
      .then(setMetrics)
      .catch((e) => setError(e?.message ?? 'Failed to load metrics'))
      .finally(() => setRefreshing(false));
  }, []);

  useEffect(() => {
    load();
    const timer = setInterval(load, 10000);
    return () => clearInterval(timer);
  }, [load]);

  const latencyData = metrics
    ? [
        { name: 'p50', value: metrics.latency_p50 },
        { name: 'p95', value: metrics.latency_p95 },
        { name: 'p99', value: metrics.latency_p99 },
      ]
    : [];

  const driftData = metrics?.drift
    ? Object.keys({
        ...metrics.drift.baseline_distribution,
        ...metrics.drift.current_distribution,
      }).map((intent) => ({
        intent: intent.replace(/_/g, ' '),
        baseline: metrics.drift.baseline_distribution[intent] ?? 0,
        current: metrics.drift.current_distribution[intent] ?? 0,
      }))
    : [];

  const driftStatus = metrics?.drift?.drift_status?.toLowerCase() ?? 'ok';
  const driftColor =
    driftStatus === 'alert'
      ? STATUS.critical
      : driftStatus === 'warning'
        ? STATUS.warning
        : STATUS.good;

  const endpointColumns: ColumnDef<EndpointMetric>[] = [
    { header: 'Endpoint', cell: (r) => <span className="font-mono text-xs">{r.endpoint}</span> },
    { header: 'Requests', cell: (r) => r.count.toLocaleString() },
    { header: 'Avg Latency', cell: (r) => `${r.avg_latency.toFixed(1)} ms` },
    { header: 'Error Rate', cell: (r) => `${(r.error_rate * 100).toFixed(2)}%` },
  ];

  return (
    <div className="space-y-6 p-8">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-white">Monitoring</h1>
          <p className="mt-1 text-sm text-slate-400">
            Live latency percentiles, throughput, and query-intent drift · auto-refreshes every 10s
          </p>
        </div>
        <button
          onClick={load}
          className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-xs text-slate-300 transition hover:border-indigo-500/50"
        >
          <RefreshCw size={13} className={refreshing ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {error && (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          title="Requests / min"
          value={metrics ? metrics.requests_per_minute.toFixed(1) : '—'}
          subtitle={`${metrics?.total_requests?.toLocaleString() ?? '—'} total`}
          icon={Zap}
          color="indigo"
        />
        <MetricCard
          title="Error Rate"
          value={metrics ? `${(metrics.error_rate * 100).toFixed(2)}%` : '—'}
          icon={AlertTriangle}
          color={metrics && metrics.error_rate > 0.05 ? 'rose' : 'emerald'}
        />
        <MetricCard
          title="Cache Hit Rate"
          value={metrics ? `${(metrics.cache_hit_rate * 100).toFixed(1)}%` : '—'}
          icon={Percent}
          color="cyan"
        />
        <MetricCard
          title="Estimated Cost"
          value={metrics ? `$${metrics.estimated_cost.toFixed(4)}` : '—'}
          subtitle="Cumulative inference + RAG"
          icon={Clock}
          color="amber"
        />
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <ChartContainer title="Latency Percentiles" subtitle="Milliseconds across all endpoints">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={latencyData} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
              <CartesianGrid stroke={CHART_GRID} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="name" stroke={CHART_TEXT} fontSize={11} tickLine={false} />
              <YAxis stroke={CHART_TEXT} fontSize={11} tickLine={false} axisLine={false} unit=" ms" />
              <Tooltip
                contentStyle={TOOLTIP_STYLE}
                formatter={(v: number) => [`${v.toFixed(1)} ms`, 'Latency']}
                cursor={{ fill: '#33415533' }}
              />
              <Bar dataKey="value" fill={CATEGORICAL[0]} radius={[4, 4, 0, 0]} maxBarSize={64} />
            </BarChart>
          </ResponsiveContainer>
        </ChartContainer>

        <ChartContainer
          title="Query Intent Drift"
          subtitle={`Baseline vs current distribution · JSD score`}
          actions={
            metrics?.drift && (
              <span
                className="inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium capitalize"
                style={{
                  color: driftColor,
                  borderColor: `${driftColor}55`,
                  backgroundColor: `${driftColor}1a`,
                }}
              >
                <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: driftColor }} />
                {driftStatus} · {metrics.drift.drift_score.toFixed(3)}
              </span>
            )
          }
        >
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={driftData} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
              <CartesianGrid stroke={CHART_GRID} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="intent" stroke={CHART_TEXT} fontSize={10} tickLine={false} />
              <YAxis
                stroke={CHART_TEXT}
                fontSize={11}
                tickLine={false}
                axisLine={false}
                tickFormatter={(v: number) => `${(v * 100).toFixed(0)}%`}
              />
              <Tooltip
                contentStyle={TOOLTIP_STYLE}
                formatter={(v: number) => `${(v * 100).toFixed(1)}%`}
                cursor={{ fill: '#33415533' }}
              />
              <Legend wrapperStyle={{ fontSize: 11 }} iconType="circle" iconSize={8} />
              <Bar dataKey="baseline" fill={SERIES.blue} radius={[3, 3, 0, 0]} maxBarSize={28} />
              <Bar dataKey="current" fill={SERIES.yellow} radius={[3, 3, 0, 0]} maxBarSize={28} />
            </BarChart>
          </ResponsiveContainer>
        </ChartContainer>
      </div>

      <div>
        <h3 className="mb-3 text-sm font-semibold text-white">Per-Endpoint Breakdown</h3>
        <DataTable
          columns={endpointColumns}
          data={metrics?.per_endpoint ?? []}
          rowKey={(r) => r.endpoint}
          emptyMessage="No requests recorded yet — try the Online Inference or RAG Assistant pages"
        />
      </div>
    </div>
  );
}
