import { Routes } from "@angular/router";
import { AdminComponent } from "./admin.component";



export const adminRoutes: Routes = [
  {
    path: '',
    component: AdminComponent,
    children: [
      {
        path: 'inventory',
        loadChildren: () => import('./inventory/inventory.routes')
      },
      {
        path: 'invoice',
        loadChildren: () => import('./invoice/invoice.routes')
      }
    ]
  },
  {
    path: '**',
    redirectTo: ''
  }
];

export default adminRoutes;
