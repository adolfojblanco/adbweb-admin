import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, computed, inject, OnInit, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { MaterialModule } from '../../shared/material/material.module';
import { HotToastService } from '@ngxpert/hot-toast';

import { LighthouseMetricCardComponent } from '../../components/lighthouse-metric-card.component';
import { LighthouseScoreCardComponent } from '../../components/lighthouse-score-card.component';
import {
  LighthouseResult,
  LIGHTHOUSE_CATEGORY_LABELS,
  LIGHTHOUSE_METRIC_LABELS,
} from '../../interfaces/seo.interface';
import { LighthouseService } from '../../services/lighthouse.service';
import { SeoService } from '../../services/seo.service';

@Component({
  selector: 'app-lighthouse-dashboard',
  imports: [
    CommonModule,
    MaterialModule,
    RouterLink,
    LighthouseScoreCardComponent,
    LighthouseMetricCardComponent,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './lighthouse-dashboard.component.html',
  styles: ``,
})
export class LighthouseDashboardComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private lighthouseApi = inject(LighthouseService);
  private seo = inject(SeoService);
  private toast = inject(HotToastService);

  readonly categoryLabels = LIGHTHOUSE_CATEGORY_LABELS;
  readonly metricLabels = LIGHTHOUSE_METRIC_LABELS;

  readonly results = signal<LighthouseResult[]>([]);
  readonly loading = signal(false);
  readonly running = signal<Set<string>>(new Set());

  readonly latest = computed<LighthouseResult | null>(() => {
    const list = this.results();
    return list.length ? list[0] : null;
  });

  readonly latestByPage = computed<Map<string, LighthouseResult>>(() => {
    const map = new Map<string, LighthouseResult>();
    for (const r of this.results()) {
      if (!map.has(r.page)) map.set(r.page, r);
    }
    return map;
  });

  ngOnInit(): void {
    const auditId = this.route.snapshot.paramMap.get('id');
    if (!auditId) {
      this.router.navigate(['/admin/seo']);
      return;
    }
    this.load(auditId);
  }

  load(auditId: string): void {
    this.loading.set(true);
    this.lighthouseApi.listForAudit(auditId, 200).subscribe({
      next: (res) => {
        this.results.set(res.results);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.toast.error('No se pudo cargar el dashboard de Lighthouse.');
      },
    });
  }

  runForPage(pageId: string): void {
    this.running.update((s) => new Set(s).add(pageId));
    this.lighthouseApi.runForPage(pageId).subscribe({
      next: () => {
        this.toast.success('Lighthouse encolado. Se actualizará al terminar.');
        // Soft refresh after a short delay.
        setTimeout(() => {
          const id = this.route.snapshot.paramMap.get('id');
          if (id) this.load(id);
          this.running.update((s) => {
            const next = new Set(s);
            next.delete(pageId);
            return next;
          });
        }, 5000);
      },
      error: () => {
        this.toast.error('No se pudo encolar Lighthouse.');
        this.running.update((s) => {
          const next = new Set(s);
          next.delete(pageId);
          return next;
        });
      },
    });
  }
}
