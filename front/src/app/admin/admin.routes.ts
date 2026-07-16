import { Routes } from "@angular/router";
import { AdminComponent } from "./admin.component";
import { DesktopComponent } from "./desktop/desktop.component";
import { staffGuard } from "./guards/staff.guard";


export const adminRoutes: Routes = [
  {
    path: '',
    component: AdminComponent,
    children: [
      {
        path: '',
        component: DesktopComponent
      },
      {
        path: 'inventory',
        loadChildren: () => import('./inventory/inventory.routes')
      },
      {
        path: 'invoice',
        loadChildren: () => import('./invoice/invoice.routes')
      },
      {
        path: 'customers',
        loadChildren: () => import('./customers/customers.routes')
      },
      {
        path: 'settings',
        loadComponent: () => import('./settings/settings.component').then(m => m.SettingsComponent),
        canActivate: [staffGuard]
      },
    ]
  },
  {
    path: '**',
    redirectTo: 'admin'
  }
];

export default adminRoutes;
