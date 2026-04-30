import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { Component, inject, OnInit, signal } from '@angular/core';
import { MaterialModule } from '../../../shared/material/material.module';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { CategoriesService } from '../../../../services/categories.service';
import { Category } from '../../../../models/category';
import { TaxService } from '../../../../services/tax.service';
import { Tax } from '../../../../models/tax';
import { ProductsService } from '../../../../services/products.service';
import { HotToastService } from '@ngxpert/hot-toast';

@Component({
  selector: 'app-dialog-product',
  imports: [MaterialModule, ReactiveFormsModule],
  templateUrl: './dialog-product.component.html',
  styles: ``,
})
export class DialogProductComponent implements OnInit {
  private fb = inject(FormBuilder);
  private data = inject(MAT_DIALOG_DATA);
  private dialogRef = inject(MatDialogRef<DialogProductComponent>)
  private toast = inject(HotToastService)
  private categoryService = inject(CategoriesService);
  private productService = inject(ProductsService)
  private taxtService = inject(TaxService);
  public taxes = signal<Tax[]>([]);
  public categories = signal<Category[]>([]);


  constructor(public MatDialogRef: MatDialogRef<DialogProductComponent>) { };

  ngOnInit() {

    this.loadCategories();
    this.loadTax();
    if (this.data) {
      this.productForm.reset(this.data);
      this.productForm.get('category')?.setValue(this.data.category.id);
      this.productForm.get('tax')?.setValue(this.data.tax.id);
    }
  }

  loadCategories() {
    this.categoryService.loadCategories().subscribe((res) => {
      this.categories.set(res)
    })
  }

  loadTax() {
    this.taxtService.loadActiveTax().subscribe((res) => {
      this.taxes.set(res);
    })
  }



  public productForm: FormGroup = this.fb.group({
    id: [null],
    name: ['', [Validators.required, Validators.minLength(3)]],
    description: ['', Validators.required],
    sale_price: ['', [Validators.required, Validators.min(0)]],
    cost_price: ['', [Validators.required, Validators.min(0)]],
    category: ['', [Validators.required]],
    tax: ['', [Validators.required]],
    active: [true]
  })


  onSubmit() {
    const product = this.productForm.value;
    if (!product.id) {
      this.productService.newProduct(product).subscribe((res) => {
        this.toast.success(`Registrado correctamente`),
          this.dialogRef.close(res)
      })

    } else {
      console.log(product);
      this.productService.editProduct(product).subscribe((res) => {
        this.dialogRef.close(res)
        this.toast.success(`Actualizado correctamente`)
      })
    }
  }







}
