import { Routes } from "@angular/router";
import { AdminComponent } from "./admin.component";
import { InventoryComponent } from "./inventory/inventory.component";



export const adminRoutes: Routes = [
  {
    path: '',
    component: AdminComponent,
    children: [
      {
        path: 'inventory',
        loadChildren: () => import('./inventory/inventory.routes')
      }
    ]
  },
  {
    path: '**',
    redirectTo: ''
  }
];

export default adminRoutes;
