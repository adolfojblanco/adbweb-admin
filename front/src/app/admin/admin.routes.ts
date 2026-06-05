import { Routes } from "@angular/router";
import { AdminComponent } from "./admin.component";
import { DesktopComponent } from "./desktop/desktop.component";


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
        path: 'clients',
        loadChildren: () => import('./clients/clients.routes')
      },
    ]
  },
  {
    path: '**',
    redirectTo: 'admin'
  }
];

export default adminRoutes;
