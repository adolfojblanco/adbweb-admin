import { Component, inject, OnInit, signal } from '@angular/core';
import { MaterialModule } from '../../shared/material/material.module';
import { IsActivePipe } from '../../../pipes/is-active.pipe';
import { PaymentMethodsService } from '../../../services/payment-methods.service';
import { PaymentsMethods } from '../../../models/payments-methods';
import { MatDialog } from '@angular/material/dialog';
import { DialogPaymentMethodsComponent } from './dialog-payment-methods/dialog-payment-methods.component';

@Component({
  selector: 'app-payment-methods',
  imports: [MaterialModule, IsActivePipe],
  templateUrl: './payment-methods.component.html',
  styles: ``,
})
export class PaymentMethodsComponent implements OnInit {
  private dialog = inject(MatDialog);
  payments = signal<PaymentsMethods[]>([]);
  private paymentServices = inject(PaymentMethodsService);
  public displayedColumns: string[] = ['name', 'active', 'actions'];



  ngOnInit(): void {
    this.loadPaymentMethods()
  }

  loadPaymentMethods() {
    this.paymentServices.getAllPaymentMethods().subscribe((res) => {
      this.payments.set(res)
    });
  }

  // /** Add a new Category */
  // newCategory() {
  //   const dialogRef = this.dialog.open(DialogCategoriesComponent, {
  //     width: '450px',
  //   });
  //   dialogRef.afterClosed().subscribe((result) => {
  //     if (result) {
  //       this.categories.update(prev => [...prev, result])
  //     }
  //   });
  // }

  // /** Edit a category */
  // editCategory(category: Category) {
  //   const dialogRef = this.dialog.open(DialogCategoriesComponent, {
  //     width: '450px',
  //     data: category
  //   })
  //   dialogRef.afterClosed().subscribe(category => {
  //     if (category) {
  //       this.categories.update(categories => categories.map(c => c.id === category.id ? category : c))
  //     }
  //   })
  // }

  newPaymentMethod() {
    const dialogRef = this.dialog.open(DialogPaymentMethodsComponent, {
      width: '450px'
    })
    dialogRef.afterClosed().subscribe((res) => {
      this.payments.update((prev) => [...prev, res])
    })
  }
  editPaymentMethod(pmethod: PaymentsMethods) {
    const dialogRef = this.dialog.open(DialogPaymentMethodsComponent, {
      width: '450px',
      data: pmethod,
    })
    dialogRef.afterClosed().subscribe((pm) => {
      this.payments.update(payments => payments.map(p => p.id === pm.id ? pm : p))
    })
  }

}
