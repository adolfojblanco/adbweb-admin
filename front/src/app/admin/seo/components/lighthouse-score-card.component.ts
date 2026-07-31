import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';

/**
 * Score card for a Lighthouse category (0-100).
 * Colors the badge green / yellow / red based on the value.
 */
@Component({
  selector: 'app-lh-score-card',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="lh-score-card h-100 d-flex flex-column">
      <span class="text-muted small text-uppercase fw-semibold">{{ label() }}</span>
      <div class="d-flex align-items-baseline gap-2 my-1">
        <span class="display-5 fw-bold" [ngClass]="valueClass()">
          {{ value() ?? '—' }}
        </span>
        @if (value() !== null) {
          <span class="text-muted small">/ 100</span>
        }
      </div>
      <span class="badge align-self-start" [ngClass]="badgeClass()">{{ verdict() }}</span>
    </div>
  `,
  styles: `
    .lh-score-card {
      padding: 1rem 1.25rem;
      border-radius: 0.75rem;
      background: #fff;
      border: 1px solid rgba(0, 0, 0, 0.06);
      box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
    }
    .lh-score-good   { color: #15803d; }
    .lh-score-medium { color: #b45309; }
    .lh-score-bad    { color: #b91c1c; }
    .lh-score-none   { color: #6b7280; }
  `,
})
export class LighthouseScoreCardComponent {
  label = input.required<string>();
  value = input<number | null>(null);

  readonly verdict = computed(() => {
    const v = this.value();
    if (v === null || v === undefined) return 'Sin datos';
    if (v >= 90) return 'Excelente';
    if (v >= 50) return 'Mejorable';
    return 'Pobre';
  });

  readonly badgeClass = computed(() => {
    const v = this.value();
    if (v === null || v === undefined) return 'bg-secondary';
    if (v >= 90) return 'bg-success';
    if (v >= 50) return 'bg-warning text-dark';
    return 'bg-danger';
  });

  readonly valueClass = computed(() => {
    const v = this.value();
    if (v === null || v === undefined) return 'lh-score-none';
    if (v >= 90) return 'lh-score-good';
    if (v >= 50) return 'lh-score-medium';
    return 'lh-score-bad';
  });
}
