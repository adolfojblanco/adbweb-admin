import { computed, inject, Injectable } from '@angular/core';
import { signal } from '@angular/core';

import { Audit, AuditStatus, Paginated } from '../interfaces/seo.interface';
import { SeoService } from '../services/seo.service';

/**
 * Cross-page SEO state container.
 *
 * Pages push their HTTP calls through this store so list/detail
 * screens can share filters, the currently selected audit and the
 * cached audit list. The store is intentionally thin: it owns
 * signals and delegates every I/O call to {@link SeoService}.
 */
@Injectable({ providedIn: 'root' })
export class SeoStore {
  private readonly api = inject(SeoService);

  readonly audits = signal<Audit[]>([]);
  readonly total = signal(0);
  readonly loading = signal(false);
  readonly statusFilter = signal<AuditStatus | ''>('');
  readonly search = signal('');

  readonly hasAudits = computed(() => this.audits().length > 0);

  loadAudits(page = 1, pageSize = 20): void {
    this.loading.set(true);
    this.api.listAudits({
      page,
      page_size: pageSize,
      status: this.statusFilter() || undefined,
      search: this.search() || undefined,
    }).subscribe({
      next: (res: Paginated<Audit>) => {
        this.audits.set(res.results);
        this.total.set(res.count);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  setStatusFilter(status: AuditStatus | ''): void {
    this.statusFilter.set(status);
    this.loadAudits();
  }

  setSearch(value: string): void {
    this.search.set(value);
  }
}
