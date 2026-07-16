import { Component, inject, OnInit, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { HotToastService } from '@ngxpert/hot-toast';
import { ClientsService } from '../../../services/clients.service';
import { Client, CustomerType } from '../../../models/client';
import { MaterialModule } from '../../shared/material/material.module';

@Component({
  selector: 'app-edit-client',
  imports: [MaterialModule, ReactiveFormsModule, RouterLink],
  templateUrl: './edit-client.component.html',
  styles: ``,
})
export class EditClientComponent implements OnInit {
  private fb = inject(FormBuilder);
  private clientsService = inject(ClientsService);
  private toast = inject(HotToastService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);

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

  loading = signal(true);
  saving = signal(false);
  clientId = signal<number | null>(null);

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (Number.isNaN(id)) {
      this.toast.error('ID de cliente inválido.');
      this.router.navigate(['/admin/clients/lists']);
      return;
    }

    this.clientId.set(id);
    this.clientsService.getById(id).subscribe({
      next: (client) => {
        this.clientForm.patchValue({
          customer_type: (client.customer_type as CustomerType) ?? CustomerType.PERSON,
          billing_name: client.billing_name ?? '',
          tax_id: client.tax_id ?? '',
          address: client.address ?? '',
          city: client.city ?? '',
          province: client.province ?? '',
          postal_code: client.postal_code ?? '',
          contact_email: client.contact_email ?? '',
          phone: client.phone ?? '',
        });
        this.loading.set(false);
      },
      error: () => {
        this.toast.error('No se pudo cargar el cliente.');
        this.router.navigate(['/admin/clients/lists']);
      },
    });
  }

  submit() {
    if (this.clientForm.invalid) {
      this.clientForm.markAllAsTouched();
      return;
    }

    const id = this.clientId();
    if (id === null) return;

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

    this.saving.set(true);
    this.clientsService.updateCustomer(id, customer).subscribe({
      next: () => {
        this.saving.set(false);
        this.toast.success('Cliente actualizado correctamente');
        this.router.navigate(['/admin/clients/lists']);
      },
      error: (err) => {
        this.saving.set(false);
        const message = err?.error?.detail || 'No se pudo actualizar el cliente.';
        this.toast.error(message);
      },
    });
  }
}
