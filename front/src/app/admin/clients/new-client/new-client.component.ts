import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { HotToastService } from '@ngxpert/hot-toast';
import { ClientsService } from '../../../services/clients.service';
import { Client, CustomerType } from '../../../models/client';
import { MaterialModule } from '../../shared/material/material.module';
import { Router } from '@angular/router';

@Component({
  selector: 'app-new-client',
  imports: [MaterialModule, ReactiveFormsModule],
  templateUrl: './new-client.component.html',
  styles: ``,
})
export class NewClientComponent {
  private fb = inject(FormBuilder);
  private clientsService = inject(ClientsService);
  private toast = inject(HotToastService);
  private router = inject(Router)

  customerTypeOptions = [
    { value: CustomerType.PERSON, label: 'Autónomo / Particular' },
    { value: CustomerType.COMPANY, label: 'Empresa' },
  ];

  clientForm = this.fb.group({
    customer_type: [CustomerType.PERSON, [Validators.required]],
    billing_name: ['', [Validators.required, Validators.minLength(3)]],
    tax_id: ['', [Validators.required, Validators.minLength(5)]],
    address: ['', [Validators.required]],
    city: ['', [Validators.required]],
    province: ['', [Validators.required]],
    postal_code: [''],
    contact_email: ['', [Validators.required, Validators.email]],
    phone: [''],
  });

  submit() {
    if (this.clientForm.invalid) {
      this.clientForm.markAllAsTouched();
      return;
    }

    const value = this.clientForm.value;
    const customer: Client = {
      customer_type: value.customer_type!,
      billing_name: value.billing_name!,
      tax_id: value.tax_id!,
      address: value.address!,
      city: value.city!,
      province: value.province!,
      postal_code: value.postal_code || null,
      contact_email: value.contact_email!,
      phone: value.phone || null,
    };

    this.clientsService.createCustomer(customer).subscribe(() => {
      this.toast.success('Cliente creado correctamente');
      this.clientForm.reset({ customer_type: CustomerType.PERSON });
      this.router.navigate(['/admin/clients/lists'])
    });
  }

}
