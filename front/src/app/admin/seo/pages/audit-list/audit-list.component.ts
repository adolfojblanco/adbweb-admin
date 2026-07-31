import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { MaterialModule } from '../../shared/material/material.module';
import { HotToastService } from '@ngxpert/hot-toast';
import { SeoService } from '../../services/seo.service';
import { Audit, AuditStatus, STATUS_CLASSES, STATUS_LABELS } from '../../interfaces/seo.interface';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-audit-list',
  imports: [MaterialModule, RouterLink, FormsModule],
  templateUrl: './audit-list.component.html',
  styles: ``,
})
export class AuditListComponent implements OnInit {
  private seo = inject(SeoService);
  private toast = inject(HotToastService);
  private router = inject(Router);

  audits = signal<Audit[]>([]);
  total = signal(0);
  page = signal(1);
  pageSize = signal(20);
  loading = signal(false);

  statusFilter = signal<AuditStatus | ''>('');
  search = signal('');

  statusOptions: AuditStatus[] = ['PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED'];

  displayedColumns: string[] = ['id', 'project', 'target', 'status', 'score', 'pages', 'issues', 'actions'];

  readonly statusLabels = STATUS_LABELS;
  readonly statusClasses = STATUS_CLASSES;

  totalPages = computed(() => Math.max(1, Math.ceil(this.total() / this.pageSize())));

  ngOnInit(): void {
    this.load();
  }

  load() {
    this.loading.set(true);
    this.seo.listAudits({
      page: this.page(),
      page_size: this.pageSize(),
      status: this.statusFilter() || undefined,
      search: this.search() || undefined,
    }).subscribe({
      next: (res) => {
        this.audits.set(res.results);
        this.total.set(res.count);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.toast.error('No se pudo cargar el listado de auditorías.');
      },
    });
  }

  applyFilters() {
    this.page.set(1);
    this.load();
  }

  changePage(next: number) {
    if (next < 1 || next > this.totalPages()) return;
    this.page.set(next);
    this.load();
  }

  deleteAudit(audit: Audit, event: Event) {
    event.stopPropagation();
    if (!confirm(`¿Eliminar la auditoría de ${audit.target_url}?`)) return;
    this.seo.deleteAudit(audit.id).subscribe(() => {
      this.toast.success('Auditoría eliminada.');
      this.load();
    });
  }

  runAgain(audit: Audit, event: Event) {
    event.stopPropagation();
    this.seo.runAudit(audit.id).subscribe({
      next: () => {
        this.toast.success('Auditoría encolada. Se actualizará automáticamente.');
        this.load();
      },
      error: (err) => this.toast.error(err?.error?.detail || 'No se pudo iniciar.'),
    });
  }

  scoreClass(score: number): string {
    if (score >= 80) return 'text-success';
    if (score >= 50) return 'text-warning';
    return 'text-danger';
  }
}
