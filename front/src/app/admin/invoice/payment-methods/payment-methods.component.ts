import { Component, inject, OnInit, signal } from '@angular/core';
import { MaterialModule } from '../../shared/material/material.module';
import { PaymentMethodsService } from '../../../services/payment-methods.service';
import { PaymentsMethods } from '../../../models/payments-methods';
import { MatDialog } from '@angular/material/dialog';
import { DialogPaymentMethodsComponent } from './dialog-payment-methods/dialog-payment-methods.component';

@Component({
  selector: 'app-payment-methods',
  imports: [MaterialModule],
  templateUrl: './payment-methods.component.html',
  styles: ``,
})
export class PaymentMethodsComponent implements OnInit {
  private dialog = inject(MatDialog);
  payments = signal<PaymentsMethods[]>([]);
  private paymentServices = inject(PaymentMethodsService);
  displayedColumns: string[] = ['id', 'name', 'is_active', 'actions'];

  ngOnInit(): void {
    this.loadPaymentMethods()
  }

  loadPaymentMethods() {
    this.paymentServices.getAllPaymentMethods().subscribe({
      next: (res) => this.payments.set(res),
      error: () => this.payments.set([]),
    });
  }

  newPaymentMethod() {
    const dialogRef = this.dialog.open(DialogPaymentMethodsComponent, {
      width: '450px'
    })
    dialogRef.afterClosed().subscribe((res) => {
      if (res) {
        this.payments.update((prev) => [...prev, res])
      }
    })
  }
  editPaymentMethod(pmethod: PaymentsMethods) {
    const dialogRef = this.dialog.open(DialogPaymentMethodsComponent, {
      width: '450px',
      data: pmethod,
    })
    dialogRef.afterClosed().subscribe((pm) => {
      if (pm) {
        this.payments.update(payments => payments.map(p => p.id === pm.id ? pm : p))
      }
    })
  }

}
