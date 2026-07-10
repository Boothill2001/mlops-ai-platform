import { useEffect, useState } from 'react';
import {
  RadialBarChart,
  RadialBar,
  PolarAngleAxis,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from 'recharts';
import { Zap, Timer, Database } from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import ChartContainer from '../components/ChartContainer';
import {
  getSuppliers,
  predictSupplierRisk,
  Supplier,
  SupplierRiskRequest,
  SupplierRiskResponse,
} from '../api/client';
import { CHART_GRID, CHART_TEXT, SERIES, STATUS, TOOLTIP_STYLE } from '../theme';

const RISK_COLOR: Record<string, string> = {
  low: STATUS.good,
  medium: STATUS.warning,
  high: STATUS.serious,
  critical: STATUS.critical,
};

const EMPTY_FORM: SupplierRiskRequest = {
  supplier_id: '',
  lead_time_days: 7,
  defect_rate: 0.02,
  late_delivery_count: 1,
  order_value: 10000,
  country: 'Vietnam',
};

export default function OnlineInference() {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [form, setForm] = useState<SupplierRiskRequest>(EMPTY_FORM);
  const [result, setResult] = useState<SupplierRiskResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getSuppliers()
      .then((s) => {
        setSuppliers(s);
        if (s.length > 0) applySupplier(s[0]);
      })
      .catch(() => setError('Failed to load sample suppliers'));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function applySupplier(s: Supplier) {
    setForm({
      supplier_id: s.supplier_id,
      lead_time_days: s.lead_time_days,
      defect_rate: s.defect_rate,
      late_delivery_count: s.late_delivery_count,
      order_value: s.order_value,
      country: s.country,
    });
  }

  function setField<K extends keyof SupplierRiskRequest>(key: K, value: SupplierRiskRequest[K]) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await predictSupplierRisk(form);
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Prediction failed');
    } finally {
      setLoading(false);
    }
  }

  const riskColor = result ? (RISK_COLOR[result.risk_level.toLowerCase()] ?? SERIES.blue) : SERIES.blue;
  const gaugeData = result ? [{ name: 'risk', value: result.risk_score * 100 }] : [];

  const explanationData = (result?.explanation ?? []).map((f) => ({
    factor: f.factor.replace(/_/g, ' '),
    impact: f.direction === 'decreases' ? -Math.abs(f.impact) : Math.abs(f.impact),
    rawValue: f.value,
    direction: f.direction,
  }));

  const inputClass =
    'w-full rounded-lg border border-slate-600 bg-slate-900 px-3 py-2 text-sm text-slate-200 outline-none transition-colors focus:border-indigo-500';

  return (
    <div className="space-y-6 p-8">
      <div>
        <h1 className="text-2xl font-semibold text-white">Online Inference</h1>
        <p className="mt-1 text-sm text-slate-400">
          Real-time supplier risk scoring with per-feature explanations
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-5">
        {/* Form */}
        <form
          onSubmit={handleSubmit}
          className="space-y-4 rounded-xl border border-slate-700/60 bg-slate-800 p-6 xl:col-span-2"
        >
          <h3 className="text-sm font-semibold text-white">Supplier Features</h3>

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Load sample supplier
            </label>
            <select
              className={inputClass}
              value={form.supplier_id}
              onChange={(e) => {
                const s = suppliers.find((x) => x.supplier_id === e.target.value);
                if (s) applySupplier(s);
                else setField('supplier_id', e.target.value);
              }}
            >
              {suppliers.map((s) => (
                <option key={s.supplier_id} value={s.supplier_id}>
                  {s.supplier_id} — {s.country}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">Supplier ID</label>
            <input
              className={inputClass}
              value={form.supplier_id}
              onChange={(e) => setField('supplier_id', e.target.value)}
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-400">
                Lead time (days)
              </label>
              <input
                type="number"
                min={0}
                className={inputClass}
                value={form.lead_time_days}
                onChange={(e) => setField('lead_time_days', Number(e.target.value))}
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-400">Defect rate</label>
              <input
                type="number"
                min={0}
                max={1}
                step={0.001}
                className={inputClass}
                value={form.defect_rate}
                onChange={(e) => setField('defect_rate', Number(e.target.value))}
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-400">
                Late deliveries
              </label>
              <input
                type="number"
                min={0}
                className={inputClass}
                value={form.late_delivery_count}
                onChange={(e) => setField('late_delivery_count', Number(e.target.value))}
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-400">
                Order value ($)
              </label>
              <input
                type="number"
                min={0}
                className={inputClass}
                value={form.order_value}
                onChange={(e) => setField('order_value', Number(e.target.value))}
              />
            </div>
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">Country</label>
            <input
              className={inputClass}
              value={form.country}
              onChange={(e) => setField('country', e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Zap size={16} />
            {loading ? 'Scoring…' : 'Score Supplier Risk'}
          </button>
        </form>

        {/* Result */}
        <div className="space-y-6 xl:col-span-3">
          {!result ? (
            <div className="flex h-full min-h-[300px] items-center justify-center rounded-xl border border-dashed border-slate-700 text-sm text-slate-500">
              Submit a supplier to see its risk assessment
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                <ChartContainer title="Risk Score" subtitle={`Supplier ${result.supplier_id}`}>
                  <div className="relative">
                    <ResponsiveContainer width="100%" height={220}>
                      <RadialBarChart
                        data={gaugeData}
                        innerRadius="70%"
                        outerRadius="95%"
                        startAngle={210}
                        endAngle={-30}
                      >
                        <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
                        <RadialBar
                          dataKey="value"
                          cornerRadius={6}
                          fill={riskColor}
                          background={{ fill: '#334155' }}
                        />
                      </RadialBarChart>
                    </ResponsiveContainer>
                    <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
                      <span className="text-4xl font-bold tabular-nums text-white">
                        {(result.risk_score * 100).toFixed(0)}
                      </span>
                      <span className="mt-1 text-xs text-slate-500">/ 100</span>
                      <div className="mt-2">
                        <StatusBadge status={result.risk_level} />
                      </div>
                    </div>
                  </div>
                </ChartContainer>

                <div className="space-y-4">
                  <div className="rounded-xl border border-slate-700/60 bg-slate-800 p-5">
                    <div className="flex items-center gap-2 text-slate-400">
                      <Timer size={15} />
                      <span className="text-xs font-medium uppercase tracking-wider">Latency</span>
                    </div>
                    <p className="mt-2 text-xl font-semibold tabular-nums text-white">
                      {result.latency_ms.toFixed(1)} ms
                    </p>
                  </div>
                  <div className="rounded-xl border border-slate-700/60 bg-slate-800 p-5">
                    <div className="flex items-center gap-2 text-slate-400">
                      <Database size={15} />
                      <span className="text-xs font-medium uppercase tracking-wider">Cache</span>
                    </div>
                    <p className="mt-2 text-xl font-semibold text-white">
                      {result.cache_hit ? 'Hit' : 'Miss'}
                    </p>
                  </div>
                  <div className="rounded-xl border border-slate-700/60 bg-slate-800 p-5">
                    <div className="text-xs font-medium uppercase tracking-wider text-slate-400">
                      Model
                    </div>
                    <p className="mt-2 truncate text-sm font-medium text-white">
                      {result.model_version}
                    </p>
                    <p className="mt-1 truncate text-xs text-slate-500">req: {result.request_id}</p>
                  </div>
                </div>
              </div>

              <ChartContainer
                title="Explanation Factors"
                subtitle="Signed feature impact on the risk score (negative bars reduce risk)"
              >
                <ResponsiveContainer width="100%" height={Math.max(180, explanationData.length * 44)}>
                  <BarChart
                    data={explanationData}
                    layout="vertical"
                    margin={{ top: 4, right: 24, left: 8, bottom: 4 }}
                  >
                    <XAxis type="number" stroke={CHART_TEXT} fontSize={11} tickLine={false} />
                    <YAxis
                      type="category"
                      dataKey="factor"
                      stroke={CHART_TEXT}
                      fontSize={11}
                      width={130}
                      tickLine={false}
                      axisLine={false}
                    />
                    <ReferenceLine x={0} stroke={CHART_GRID} />
                    <Tooltip
                      contentStyle={TOOLTIP_STYLE}
                      cursor={{ fill: '#33415533' }}
                      formatter={(v: number, _n, entry) => [
                        `${v >= 0 ? '+' : ''}${v.toFixed(3)} (value: ${entry?.payload?.rawValue})`,
                        'Impact',
                      ]}
                    />
                    <Bar dataKey="impact" barSize={14} radius={[0, 4, 4, 0]}>
                      {explanationData.map((d, i) => (
                        <Cell key={i} fill={d.impact >= 0 ? SERIES.red : SERIES.blue} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
                <div className="mt-2 flex gap-5 text-xs text-slate-400">
                  <span className="flex items-center gap-1.5">
                    <span className="h-2.5 w-2.5 rounded-sm" style={{ backgroundColor: SERIES.red }} />
                    Increases risk
                  </span>
                  <span className="flex items-center gap-1.5">
                    <span className="h-2.5 w-2.5 rounded-sm" style={{ backgroundColor: SERIES.blue }} />
                    Decreases risk
                  </span>
                </div>
              </ChartContainer>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
