import { Routes } from "@angular/router";
import { InventoryComponent } from "./inventory.component";
import { ProductsComponent } from "./products/products.component";
import { CategoriesComponent } from "./categories/categories.component";



export const inventoryRoutes: Routes = [
  {
    path: '',
    component: InventoryComponent,
    children: [
      {
        path: 'products',
        component: ProductsComponent
      },
      {
        path: 'categories',
        component: CategoriesComponent
      }
    ]
  },
  {
    path: '**',
    redirectTo: 'admin'
  }

]

export default inventoryRoutes;
