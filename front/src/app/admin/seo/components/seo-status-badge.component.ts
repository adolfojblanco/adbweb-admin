import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';

import { AuditStatus, STATUS_CLASSES, STATUS_LABELS } from '../interfaces/seo.interface';

@Component({
  selector: 'app-seo-status-badge',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<span class="badge" [ngClass]="cls()">{{ label() }}</span>`,
  styles: ``,
})
export class SeoStatusBadgeComponent {
  status = input.required<AuditStatus>();

  readonly label = computed(() => STATUS_LABELS[this.status()]);
  readonly cls = computed(() => STATUS_CLASSES[this.status()]);
}
