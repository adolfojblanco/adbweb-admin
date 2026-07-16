import { Routes } from "@angular/router";
import { InvoiceComponent } from "./invoice.component";
import { NewInvoiceComponent } from "./new-invoice/new-invoice.component";
import { PaymentMethodsComponent } from "./payment-methods/payment-methods.component";
import { SupplierComponent } from "./supplier/supplier.component";
import { ListInvoiceComponent } from './list-invoice/list-invoice.component';
import { DetailInvoiceComponent } from './detail-invoice/detail-invoice.component';
import { EditInvoiceComponent } from './edit-invoice/edit-invoice.component';




export const invoiceRoutes: Routes = [
  {
    path: '',
    component: InvoiceComponent,
    children: [
      {
        path: '',
        pathMatch: 'full',
        redirectTo: 'list-invoice'
      },
      {
        path: 'new',
        component: NewInvoiceComponent
      },
      {
        path: 'list-invoice',
        component: ListInvoiceComponent
      },
      {
        path: 'detailinvoice/:id',
        component: DetailInvoiceComponent
      },
      {
        path: 'editinvoice/:id',
        component: EditInvoiceComponent
      },
      {
        path: 'payment-methods',
        component: PaymentMethodsComponent
      },
      {
        path: 'suppliers',
        component: SupplierComponent
      }
    ]
  },
  {
    path: '**',
    redirectTo: ''
  }

]


export default invoiceRoutes;
