import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';

import { IssueSeverity, SEVERITY_CLASSES, SEVERITY_LABELS } from '../interfaces/seo.interface';

@Component({
  selector: 'app-seo-severity-badge',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<span class="badge" [ngClass]="cls()">{{ label() }}</span>`,
  styles: ``,
})
export class SeoSeverityBadgeComponent {
  severity = input.required<IssueSeverity>();

  readonly label = computed(() => SEVERITY_LABELS[this.severity()]);
  readonly cls = computed(() => SEVERITY_CLASSES[this.severity()]);
}
