import { Routes } from "@angular/router";
import { CustomersComponent } from "./customers.component";
import { NewCustomerComponent } from "./new-customer/new-customer.component";



export const customerRoutes: Routes = [
  {
    path: '',
    component: CustomersComponent,
    children: [
      {
        path: 'new',
        component: NewCustomerComponent
      },
        {
        path: 'list',
        component: NewCustomerComponent
      }
    ]
  },
    {
    path: '**',
    redirectTo: 'customers'
  }
]


export default customerRoutes
