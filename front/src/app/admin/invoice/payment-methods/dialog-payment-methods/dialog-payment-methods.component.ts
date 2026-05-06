import { Component, inject, OnInit } from '@angular/core';
import { MaterialModule } from '../../../shared/material/material.module';
import { PaymentMethodsService } from '../../../../services/payment-methods.service';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { HotToastService } from '@ngxpert/hot-toast';
import { PaymentsMethods } from '../../../../models/payments-methods';

@Component({
  selector: 'app-dialog-payment-methods',
  imports: [MaterialModule, ReactiveFormsModule],
  templateUrl: './dialog-payment-methods.component.html',
  styles: ``,
})
export class DialogPaymentMethodsComponent implements OnInit {
  private paymentService = inject(PaymentMethodsService);
  private fb = inject(FormBuilder);
  private data = inject(MAT_DIALOG_DATA);
  private toast = inject(HotToastService)

  constructor(public dialogRef: MatDialogRef<DialogPaymentMethodsComponent>) { }


  ngOnInit(): void {
    if (this.data) {
      this.paymentMethodForm.reset(this.data)
    }
  }

  paymentMethodForm: FormGroup = this.fb.group({
    id: null,
    name: ['', [Validators.required]],
    active: [true]
  })

  submit() {

    if (this.paymentMethodForm.invalid) return;
    const paymentMethod: PaymentsMethods = { ...this.paymentMethodForm.value }
    if (paymentMethod.id) {
      this.paymentService.editPaymentMethod(paymentMethod).subscribe((res) => {
        this.toast.success(`${paymentMethod.name}, Editado correctamente`);
        this.dialogRef.close(res)
      })
    } else {
      this.paymentService.newPaymentMethod(paymentMethod).subscribe((res) => {
        this.toast.success(`${paymentMethod.name}, Registrado correctamente`);
        this.dialogRef.close(res)
      })
    }
  }




}
