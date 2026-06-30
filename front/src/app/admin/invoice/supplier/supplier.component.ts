import { Component, ElementRef, inject, signal, ViewChild, viewChild } from '@angular/core';
import { MaterialModule } from '../../shared/material/material.module';
import { IsActivePipe } from '../../../pipes/is-active.pipe';
import { SuppliersService } from '../../../services/suppliers.service';
import { Supplier } from '../../../models/suppliers';
import * as bootstrap from 'bootstrap';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { email } from '@angular/forms/signals';
import { HotToastService } from '@ngxpert/hot-toast';

@Component({
  selector: 'app-supplier',
  imports: [MaterialModule, IsActivePipe, ReactiveFormsModule],
  templateUrl: './supplier.component.html',
  styles: ``,
})
export class SupplierComponent {
  @ViewChild('supplierModal') modalElement!: ElementRef;
  private toast = inject(HotToastService);
  private fb = inject(FormBuilder)
  supplierService = inject(SuppliersService);
  suppliers = signal<Supplier[]>([])
  modalInstance: any;
  modalTitle = signal('')
  displayedColumns: string[] = ['name', 'phone', 'email', 'is_active', 'actions'];

  ngOnInit() {
    this.getSuppliers()
  }

  getSuppliers() {
    this.supplierService.getAllSuppliers().subscribe((res:Supplier[]) => {
      this.suppliers.set(res)
    })
  }

  newSupplier() : void{
   this.openModalSupplier('Nuevo Proveedor:');
   this.supplierForm.reset();
  }

  editSupplier(supplier: Supplier) {
    this.supplierForm.reset(supplier)
    this.openModalSupplier('Edición de proveedor:')
  }

  supplierForm: FormGroup = this.fb.group({
    id: [null],
    name: ['', [Validators.required]],
    email: ['', [Validators.email]],
    phone: ['',],
    is_active: [false]
  })

  onSubmit(){
    if (this.supplierForm.invalid) {
      this.supplierForm.markAllAsTouched();
      return
    }
    const supplier: Supplier = this.supplierForm.value;

    if (supplier.id != null) {
      this.supplierService.editSupplier(supplier).subscribe((res) => {
        this.suppliers.update((prev) => prev.map(item => item.id === supplier.id ? supplier: item))
        this.toast.success(`${supplier.name}, editado correctamente`);
        this.closeModalSupplier();
      })
    }else{
      this.supplierService.newSupplier(supplier).subscribe((res) => {
        this.toast.success(`${supplier.name}, registrado correctamente`);
        this.suppliers.update((prev) => [...prev, supplier])
        this.closeModalSupplier()
      })
    }
  }

  openModalSupplier(title: string) {
    this.modalTitle.set(title)
    this.modalInstance = new bootstrap.Modal(this.modalElement.nativeElement);
    this.modalInstance.show();
  }

  closeModalSupplier() {
    if (this.modalInstance) {
      this.modalTitle.set('');
      this.supplierForm.reset();
      this.modalInstance.hide();
    }
  }
}
