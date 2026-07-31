import { Component, computed, inject, OnDestroy, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { MaterialModule } from '../../shared/material/material.module';
import { HotToastService } from '@ngxpert/hot-toast';
import { SeoService } from '../../services/seo.service';
import {
  Audit, AuditStatus, CATEGORY_LABELS, Issue, IssueCategory, IssueSeverity,
  Page, SEVERITY_CLASSES, SEVERITY_LABELS, STATUS_CLASSES, STATUS_LABELS,
} from '../../interfaces/seo.interface';

type Tab = 'issues' | 'pages';

@Component({
  selector: 'app-audit-detail',
  imports: [MaterialModule, RouterLink, FormsModule],
  templateUrl: './audit-detail.component.html',
  styles: ``,
})
export class AuditDetailComponent implements OnInit, OnDestroy {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private seo = inject(SeoService);
  private toast = inject(HotToastService);

  audit = signal<Audit | null>(null);
  issues = signal<Issue[]>([]);
  pages = signal<Page[]>([]);
  issuesCount = signal(0);
  pagesCount = signal(0);
  tab = signal<Tab>('issues');
  loading = signal(false);

  categoryFilter = signal<IssueCategory | ''>('');
  severityFilter = signal<IssueSeverity | ''>('');

  private pollHandle: ReturnType<typeof setInterval> | null = null;

  readonly statusLabels = STATUS_LABELS;
  readonly statusClasses = STATUS_CLASSES;
  readonly severityLabels = SEVERITY_LABELS;
  readonly severityClasses = SEVERITY_CLASSES;
  readonly categoryLabels = CATEGORY_LABELS;

  readonly issueColumns = ['severity', 'code', 'category', 'page_url', 'message'];
  readonly pageColumns = ['status', 'url', 'title', 'response_time_ms', 'images_without_alt'];

  readonly issueCategoryOptions: IssueCategory[] = [
    'META', 'HEADINGS', 'IMAGES', 'LINKS', 'PERFORMANCE', 'STATUS', 'INDEXABILITY', 'SECURITY',
  ];
  readonly severityOptions: IssueSeverity[] = ['INFO', 'WARNING', 'ERROR', 'CRITICAL'];

  readonly isRunning = computed(() => {
    const status = this.audit()?.status;
    return status === 'PENDING' || status === 'RUNNING';
  });

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (Number.isNaN(id)) {
      this.toast.error('ID inválido.');
      this.router.navigate(['/admin/seo/audit-list']);
      return;
    }
    this.loadAll(id);
    this.pollHandle = setInterval(() => {
      const current = this.audit();
      if (current && (current.status === 'PENDING' || current.status === 'RUNNING')) {
        this.refreshAudit(id);
      }
    }, 3000);
  }

  ngOnDestroy(): void {
    if (this.pollHandle) clearInterval(this.pollHandle);
  }

  loadAll(id: number) {
    this.loading.set(true);
    this.seo.getAudit(id).subscribe({
      next: (audit) => {
        this.audit.set(audit);
        this.loading.set(false);
        this.loadIssues(id);
        this.loadPages(id);
      },
      error: () => {
        this.loading.set(false);
        this.toast.error('No se pudo cargar la auditoría.');
        this.router.navigate(['/admin/seo/audit-list']);
      },
    });
  }

  refreshAudit(id: number) {
    this.seo.getAudit(id).subscribe({
      next: (audit) => {
        this.audit.set(audit);
        if (audit.status === 'COMPLETED' || audit.status === 'FAILED') {
          this.loadIssues(id);
          this.loadPages(id);
        }
      },
    });
  }

  loadIssues(id: number) {
    this.seo.getIssues(id, {
      severity: this.severityFilter() || undefined,
      category: this.categoryFilter() || undefined,
    }).subscribe({
      next: (res) => {
        this.issues.set(res.results);
        this.issuesCount.set(res.count);
      },
    });
  }

  loadPages(id: number) {
    this.seo.getPages(id).subscribe({
      next: (res) => {
        this.pages.set(res.results);
        this.pagesCount.set(res.count);
      },
    });
  }

  applyFilters() {
    const id = this.audit()?.id;
    if (id) this.loadIssues(id);
  }

  runAgain() {
    const id = this.audit()?.id;
    if (!id) return;
    this.seo.runAudit(id).subscribe({
      next: () => {
        this.toast.success('Auditoría reencolada.');
        this.loadAll(id);
      },
      error: (err) => this.toast.error(err?.error?.detail || 'No se pudo relanzar.'),
    });
  }

  scoreClass(score: number): string {
    if (score >= 80) return 'text-success';
    if (score >= 50) return 'text-warning';
    return 'text-danger';
  }
}
