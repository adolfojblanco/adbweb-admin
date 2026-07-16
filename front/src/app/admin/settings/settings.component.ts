import { Component, ElementRef, inject, OnInit, signal, ViewChild } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { HotToastService } from '@ngxpert/hot-toast';
import { CompanyService } from '../../services/company.service';
import { MaterialModule } from '../shared/material/material.module';

@Component({
  selector: 'app-settings',
  imports: [MaterialModule, ReactiveFormsModule],
  templateUrl: './settings.component.html',
  styles: ``,
})
export class SettingsComponent implements OnInit {
  private fb = inject(FormBuilder);
  private companyService = inject(CompanyService);
  private toast = inject(HotToastService);

  @ViewChild('logoInput') logoInput!: ElementRef<HTMLInputElement>;

  loading = signal(true);
  saving = signal(false);
  logoUrl = signal<string | null>(null);

  companyForm = this.fb.group({
    name: ['', [Validators.required]],
    email_company: ['', [Validators.required, Validators.email]],
    phone: ['', [Validators.required]],
    website: [''],
    address: [''],
    city: ['', [Validators.required]],
    state: ['', [Validators.required]],
    postal_code: [''],
  });

  ngOnInit(): void {
    this.companyService.getCompany().subscribe({
      next: (company) => {
        this.companyForm.patchValue({
          name: company.name ?? '',
          email_company: company.email_company ?? '',
          phone: company.phone ?? '',
          website: company.website ?? '',
          address: company.address ?? '',
          city: company.city ?? '',
          state: company.state ?? '',
          postal_code: company.postal_code ?? '',
        });
        this.logoUrl.set(company.logo ?? null);
        this.loading.set(false);
      },
      error: (err) => {
        this.toast.error(err?.error?.detail || 'No se pudo cargar la empresa.');
        this.loading.set(false);
      },
    });
  }

  triggerLogoInput() {
    this.logoInput.nativeElement.click();
  }

  onLogoChange(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => this.logoUrl.set((e.target?.result as string) ?? null);
      reader.readAsDataURL(file);
    }
  }

  submit() {
    if (this.companyForm.invalid) {
      this.companyForm.markAllAsTouched();
      return;
    }

    const formData = new FormData();
    const value = this.companyForm.value;
    Object.entries(value).forEach(([key, val]) => {
      if (val !== null && val !== undefined && val !== '') {
        formData.append(key, val as string);
      }
    });

    const logoFile = this.logoInput.nativeElement.files?.[0];
    if (logoFile) {
      formData.append('logo', logoFile);
    }

    this.saving.set(true);
    this.companyService.updateCompany(formData).subscribe({
      next: (company) => {
        this.saving.set(false);
        this.toast.success('Datos de la empresa actualizados');
        if (company.logo) {
          this.logoUrl.set(`${company.logo}?v=${Date.now()}`);
        }
      },
      error: (err) => {
        this.saving.set(false);
        const message = err?.error?.detail || 'No se pudo actualizar la empresa.';
        this.toast.error(message);
      },
    });
  }
}
