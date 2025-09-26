import { Routes } from "@angular/router";
import { InventoryComponent } from "./inventory.component";



export const inventoryRoutes : Routes = [
    {
      path: '',
      component: InventoryComponent
    },
    {
      path: '**',
      redirectTo: 'login'
    }

]

export default inventoryRoutes;
