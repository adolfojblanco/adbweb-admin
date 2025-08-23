import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: 'auth',
    loadChildren: () => import('./auth/auth.routes')
  },
  {
    path: 'admin',
    loadChildren: () => import('./admin/admin.routes')
  },
  {
    path: '**',
    redirectTo: '/auth/login'
  }
];
