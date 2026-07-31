import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';

import { LIGHTHOUSE_METRIC_UNITS } from '../interfaces/seo.interface';
import { LighthouseMetricKey } from '../interfaces/seo.interface';

/**
 * Metric card for one Core Web Vital (CLS, LCP, INP, FCP, TTFB, Speed Index).
 * Color comes from Google's "good / needs improvement / poor" thresholds.
 */
@Component({
  selector: 'app-lh-metric-card',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="lh-metric-card h-100 d-flex flex-column">
      <span class="text-muted small text-uppercase fw-semibold">{{ label() }}</span>
      <div class="d-flex align-items-baseline gap-1 my-1">
        <span class="display-6 fw-bold" [ngClass]="valueClass()">
          {{ display() }}
        </span>
        @if (unit()) {
          <span class="text-muted small">{{ unit() }}</span>
        }
      </div>
      <span class="badge align-self-start" [ngClass]="badgeClass()">{{ verdict() }}</span>
    </div>
  `,
  styles: `
    .lh-metric-card {
      padding: 1rem 1.25rem;
      border-radius: 0.75rem;
      background: #fff;
      border: 1px solid rgba(0, 0, 0, 0.06);
      box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
    }
    .lh-good   { color: #15803d; }
    .lh-medium { color: #b45309; }
    .lh-bad    { color: #b91c1c; }
    .lh-none   { color: #6b7280; }
  `,
})
export class LighthouseMetricCardComponent {
  metric = input.required<LighthouseMetricKey>();
  label = input.required<string>();
  value = input<number | null>(null);

  readonly unit = computed(() => LIGHTHOUSE_METRIC_UNITS[this.metric()]);

  readonly display = computed(() => {
    const v = this.value();
    if (v === null || v === undefined) return '—';
    if (this.metric() === 'cls') return v.toFixed(3);
    return Math.round(v).toString();
  });

  readonly verdict = computed(() => {
    const v = this.value();
    if (v === null || v === undefined) return 'Sin datos';
    if (this.isGood(v)) return 'Bueno';
    if (this.isMedium(v)) return 'Mejorable';
    return 'Pobre';
  });

  readonly badgeClass = computed(() => {
    const v = this.value();
    if (v === null || v === undefined) return 'bg-secondary';
    if (this.isGood(v)) return 'bg-success';
    if (this.isMedium(v)) return 'bg-warning text-dark';
    return 'bg-danger';
  });

  readonly valueClass = computed(() => {
    const v = this.value();
    if (v === null || v === undefined) return 'lh-none';
    if (this.isGood(v)) return 'lh-good';
    if (this.isMedium(v)) return 'lh-medium';
    return 'lh-bad';
  });

  // Thresholds from web.dev / Lighthouse.
  private isGood(v: number): boolean {
    switch (this.metric()) {
      case 'cls': return v <= 0.1;
      case 'lcp': return v <= 2500;
      case 'inp': return v <= 200;
      case 'fcp': return v <= 1800;
      case 'ttfb': return v <= 800;
      case 'speed_index': return v <= 3400;
    }
  }

  private isMedium(v: number): boolean {
    switch (this.metric()) {
      case 'cls': return v <= 0.25;
      case 'lcp': return v <= 4000;
      case 'inp': return v <= 500;
      case 'fcp': return v <= 3000;
      case 'ttfb': return v <= 1800;
      case 'speed_index': return v <= 5800;
    }
  }
}
