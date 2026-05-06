import { Routes } from "@angular/router";
import { InvoiceComponent } from "./invoice.component";
import { NewInvoiceComponent } from "./new-invoice/new-invoice.component";
import { PaymentMethodsComponent } from "./payment-methods/payment-methods.component";




export const invoiceRoutes: Routes = [
  {
    path: '',
    component: InvoiceComponent,
    children: [
      {
        path: 'new',
        component: NewInvoiceComponent
      },
      {
        path: 'payment-methods',
        component: PaymentMethodsComponent
      }
    ]
  }
]


export default invoiceRoutes;
