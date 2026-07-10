import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 60000,
});

// ---------- Types ----------

export interface ExplanationFactor {
  factor: string;
  value: number | string;
  impact: number;
  direction: 'increases' | 'decreases' | string;
}

export interface SupplierRiskRequest {
  supplier_id: string;
  lead_time_days: number;
  defect_rate: number;
  late_delivery_count: number;
  order_value: number;
  country: string;
}

export interface SupplierRiskResponse {
  request_id: string;
  supplier_id: string;
  risk_score: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical' | string;
  model_version: string;
  latency_ms: number;
  cache_hit: boolean;
  explanation: ExplanationFactor[];
}

export interface Supplier {
  supplier_id: string;
  lead_time_days: number;
  defect_rate: number;
  late_delivery_count: number;
  order_value: number;
  country: string;
  [key: string]: unknown;
}

export interface BatchRunRequest {
  data_csv: string;
  chunk_size: number;
}

export interface BatchRunResponse {
  job_id: string;
  status: string;
  message?: string;
}

export interface BatchJobResult {
  supplier_id?: string;
  risk_score?: number;
  risk_level?: string;
  [key: string]: unknown;
}

export interface BatchJob {
  job_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | string;
  total_records: number;
  processed_records: number;
  failed_records: number;
  progress_pct: number;
  created_at: string;
  completed_at: string | null;
  results?: BatchJobResult[];
}

export interface RagQueryRequest {
  user_id: string;
  role: string;
  query: string;
  top_k: number;
}

export interface Citation {
  doc_id: string;
  title: string;
  chunk_text: string;
  relevance_score: number;
}

export interface RagQueryResponse {
  answer: string;
  citations: Citation[];
  grounded: boolean;
  latency_ms: number;
  cache_hit: boolean;
  permission_filtered_count: number;
  chunks_retrieved: number;
  request_id: string;
}

export interface RagDocument {
  doc_id?: string;
  title: string;
  [key: string]: unknown;
}

export interface DriftInfo {
  drift_score: number;
  drift_status: string;
  baseline_distribution: Record<string, number>;
  current_distribution: Record<string, number>;
  sample_size: number;
}

export interface EndpointMetric {
  endpoint: string;
  count: number;
  avg_latency: number;
  error_rate: number;
}

export interface MonitoringMetrics {
  latency_p50: number;
  latency_p95: number;
  latency_p99: number;
  requests_per_minute: number;
  error_rate: number;
  cache_hit_rate: number;
  estimated_cost: number;
  rag_citation_rate: number;
  total_requests: number;
  drift: DriftInfo;
  per_endpoint: EndpointMetric[];
}

export interface HistoryRecord {
  request_id?: string;
  endpoint?: string;
  latency_ms?: number;
  timestamp?: string;
  status?: string;
  cache_hit?: boolean;
  [key: string]: unknown;
}

export interface EvaluationRunRequest {
  top_k: number;
  role: string;
}

export interface FailedCase {
  question: string;
  recall: number;
  expected_docs: string[];
  retrieved_docs: string[];
}

export interface EvaluationResult {
  recall_at_k: number;
  precision_at_k: number;
  faithfulness: number;
  citation_accuracy: number;
  total_questions: number;
  passed_questions: number;
  failed_cases: FailedCase[];
  regression_detected: boolean;
}

export interface GoldenQuestion {
  question: string;
  expected_docs?: string[];
  [key: string]: unknown;
}

// ---------- Endpoints ----------

export async function predictSupplierRisk(
  body: SupplierRiskRequest,
): Promise<SupplierRiskResponse> {
  const { data } = await api.post<SupplierRiskResponse>('/inference/supplier-risk', body);
  return data;
}

export async function getSuppliers(): Promise<Supplier[]> {
  const { data } = await api.get<Supplier[]>('/inference/suppliers');
  return data;
}

export async function runBatch(body: BatchRunRequest): Promise<BatchRunResponse> {
  const { data } = await api.post<BatchRunResponse>('/batch/run', body);
  return data;
}

export async function runSampleBatch(): Promise<BatchRunResponse> {
  const { data } = await api.post<BatchRunResponse>('/batch/run-sample');
  return data;
}

export async function getBatchJobs(): Promise<BatchJob[]> {
  const { data } = await api.get<BatchJob[]>('/batch/jobs');
  return data;
}

export async function getBatchJob(jobId: string): Promise<BatchJob> {
  const { data } = await api.get<BatchJob>(`/batch/jobs/${jobId}`);
  return data;
}

export async function ragQuery(body: RagQueryRequest): Promise<RagQueryResponse> {
  const { data } = await api.post<RagQueryResponse>('/rag/query', body);
  return data;
}

export async function getRagDocuments(): Promise<RagDocument[]> {
  const { data } = await api.get<RagDocument[]>('/rag/documents');
  return data;
}

export async function getMonitoringMetrics(): Promise<MonitoringMetrics> {
  const { data } = await api.get<MonitoringMetrics>('/monitoring/metrics');
  return data;
}

export async function getMonitoringHistory(): Promise<HistoryRecord[]> {
  const { data } = await api.get<HistoryRecord[]>('/monitoring/history');
  return data;
}

export async function runEvaluation(body: EvaluationRunRequest): Promise<EvaluationResult> {
  const { data } = await api.post<EvaluationResult>('/evaluation/run', body);
  return data;
}

export async function getGoldenQuestions(): Promise<GoldenQuestion[]> {
  const { data } = await api.get<GoldenQuestion[]>('/evaluation/golden-questions');
  return data;
}

export default api;
