import { Routes } from '@angular/router';

export const seoRoutes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('../pages/audit-list/audit-list.component').then(m => m.AuditListComponent),
  },
  {
    path: 'audit-run',
    loadComponent: () =>
      import('../pages/audit-run/audit-run.component').then(m => m.AuditRunComponent),
  },
  {
    path: 'audit-detail/:id',
    loadComponent: () =>
      import('../pages/audit-detail/audit-detail.component').then(m => m.AuditDetailComponent),
  },
  {
    path: 'audit-detail/:id/lighthouse',
    loadComponent: () =>
      import('../pages/lighthouse/lighthouse-dashboard.component').then(
        m => m.LighthouseDashboardComponent,
      ),
  },
];
