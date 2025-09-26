import { Routes } from "@angular/router";
import { AdminComponent } from "./admin.component";
import { InventoryComponent } from "./inventory/inventory.component";



export const adminRoutes: Routes = [
  {
    path: '',
    component: AdminComponent,
  },
  {
    path: 'inventory',
    component: InventoryComponent
  },
  {
    path: '**',
    redirectTo: '/admin',
  },

];

export default adminRoutes;
