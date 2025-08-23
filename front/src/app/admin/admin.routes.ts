import { Routes } from "@angular/router";
import { AdminComponent } from "./admin.component";



export const adminRoutes: Routes = [
  {
    path: '',
    component: AdminComponent,
    children: [

    ]
  },
  {
    path: '**',
    redirectTo: '/admin',
  },

];

export default adminRoutes;
