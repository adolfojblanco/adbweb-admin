export type AuditStatus = 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
export type IssueSeverity = 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
export type IssueCategory =
  | 'META' | 'HEADINGS' | 'IMAGES' | 'LINKS'
  | 'PERFORMANCE' | 'STATUS' | 'INDEXABILITY' | 'SECURITY';

export interface Project {
  id: number;
  name: string;
  domain: string;
  created_at: string;
  updated_at: string;
}

export interface Audit {
  id: number;
  project: number;
  project_name: string;
  target_url: string;
  status: AuditStatus;
  max_pages: number;
  started_at: string | null;
  completed_at: string | null;
  pages_crawled: number;
  issues_count: number;
  score: number;
  error_message: string;
  duration_seconds: number | null;
  created_at: string;
  updated_at: string;
}

export interface Page {
  id: number;
  url: string;
  status_code: number;
  title: string;
  meta_description: string;
  h1: string;
  content_type: string;
  content_length: number;
  response_time_ms: number;
  internal_links: number;
  external_links: number;
  images_total: number;
  images_without_alt: number;
  is_indexable: boolean;
}

export interface Issue {
  id: number;
  page: number | null;
  page_url: string | null;
  severity: IssueSeverity;
  category: IssueCategory;
  code: string;
  message: string;
}

export interface Paginated<T> {
  count: number;
  page?: number;
  page_size?: number;
  results: T[];
}

export const STATUS_LABELS: Record<AuditStatus, string> = {
  PENDING: 'Pendiente',
  RUNNING: 'En curso',
  COMPLETED: 'Completado',
  FAILED: 'Fallido',
  CANCELLED: 'Cancelado',
};

export const STATUS_CLASSES: Record<AuditStatus, string> = {
  PENDING: 'bg-secondary',
  RUNNING: 'bg-info text-white',
  COMPLETED: 'bg-success',
  FAILED: 'bg-danger',
  CANCELLED: 'bg-dark text-white',
};

export const SEVERITY_LABELS: Record<IssueSeverity, string> = {
  INFO: 'Info',
  WARNING: 'Advertencia',
  ERROR: 'Error',
  CRITICAL: 'Crítico',
};

export const SEVERITY_CLASSES: Record<IssueSeverity, string> = {
  INFO: 'bg-secondary',
  WARNING: 'bg-warning text-dark',
  ERROR: 'bg-danger',
  CRITICAL: 'bg-dark text-white',
};

export const CATEGORY_LABELS: Record<IssueCategory, string> = {
  META: 'Meta etiquetas',
  HEADINGS: 'Encabezados',
  IMAGES: 'Imágenes',
  LINKS: 'Enlaces',
  PERFORMANCE: 'Rendimiento',
  STATUS: 'Estado HTTP',
  INDEXABILITY: 'Indexabilidad',
  SECURITY: 'Seguridad',
};

// -------------------------------------------------------------------- //
// Lighthouse
// -------------------------------------------------------------------- //
export interface LighthouseResult {
  id: string;
  page: string;
  page_url: string;
  performance_score: number | null;
  accessibility_score: number | null;
  seo_score: number | null;
  best_practices_score: number | null;
  cls: number | null;
  lcp: number | null;
  inp: number | null;
  fcp: number | null;
  ttfb: number | null;
  speed_index: number | null;
  lighthouse_version: string;
  user_agent: string;
  run_at: string;
  error_message: string;
}

export type LighthouseCategory =
  | 'performance'
  | 'accessibility'
  | 'seo'
  | 'best_practices';

export type LighthouseMetricKey = 'cls' | 'lcp' | 'inp' | 'fcp' | 'ttfb' | 'speed_index';

export const LIGHTHOUSE_CATEGORY_LABELS: Record<LighthouseCategory, string> = {
  performance: 'Performance',
  accessibility: 'Accessibility',
  seo: 'SEO',
  best_practices: 'Best Practices',
};

export const LIGHTHOUSE_METRIC_LABELS: Record<LighthouseMetricKey, string> = {
  cls: 'CLS',
  lcp: 'LCP',
  inp: 'INP',
  fcp: 'FCP',
  ttfb: 'TTFB',
  speed_index: 'Speed Index',
};

export const LIGHTHOUSE_METRIC_UNITS: Record<LighthouseMetricKey, string> = {
  cls: '',
  lcp: 'ms',
  inp: 'ms',
  fcp: 'ms',
  ttfb: 'ms',
  speed_index: 'ms',
};
