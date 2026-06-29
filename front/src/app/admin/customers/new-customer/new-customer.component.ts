import { Component, inject } from '@angular/core';
import { MaterialModule } from '../../shared/material/material.module';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { CustomerType } from '../../../models/customer-type.enum';
import { Customer } from '../../../models/customer';

@Component({
  selector: 'app-new-customer',
  imports: [MaterialModule, ReactiveFormsModule],
  templateUrl: './new-customer.component.html',
  styles: ``,
})
export class NewCustomerComponent {
  private fb = inject(FormBuilder)
  customer!: Customer;

  customerForm: FormGroup = this.fb.group({
    customer_type: [CustomerType.PERSON, Validators.required],
    billing_name: ['', [Validators.required, Validators.maxLength(255)]],
    tax_id: ['', [Validators.required, Validators.maxLength(50)]],
    address: ['', [Validators.required, Validators.maxLength(255)]],
    city: ['', Validators.required],
    province: ['', Validators.required],
    postal_code: [''],
    country: ['España', Validators.required],
    contact_email: ['', [Validators.required, Validators.email]],
    phone: ['']
  })


  submit() {
    if (this.customerForm.invalid) {
      this.customerForm.markAllAsTouched();
      return;
    }
    console.log(this.customerForm.value)
  }

  resetForm() {
    this.customerForm.
  }


}
