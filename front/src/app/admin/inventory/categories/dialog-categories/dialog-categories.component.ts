import { Component, inject, OnInit } from '@angular/core';
import { MaterialModule } from '../../../shared/material/material.module';
import { HotToastService } from '@ngxpert/hot-toast';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { CategoriesService } from '../../../../services/categories.service';
import { Category } from '../../../../models/category';

@Component({
  selector: 'app-dialog-categories',
  imports: [MaterialModule, ReactiveFormsModule],
  templateUrl: './dialog-categories.component.html',
  styles: ``,
})
export class DialogCategoriesComponent implements OnInit {
  private categoryService = inject(CategoriesService);
  private fb = inject(FormBuilder);
  private data = inject(MAT_DIALOG_DATA)
  private toast = inject(HotToastService);

  constructor(public dialogRef: MatDialogRef<DialogCategoriesComponent>) { };

  ngOnInit(): void {
    if (this.data) {
      this.categoryForm.reset(this.data)
    }
  }

  public categoryForm: FormGroup = this.fb.group({
    id: [null],
    name: ['', [Validators.required, Validators.minLength(3)]],
    is_active: [true]
  })

  submit() {
    if (this.categoryForm.invalid) return;
    const category: Category = { ...this.categoryForm.value };

    if (category.id) {
      this.categoryService.editCategory(category).subscribe((res) => {
        this.toast.success(`${category.name}, actualizada correctamente`)
        this.dialogRef.close(res)
      });
    } else {
      this.categoryService.newCategory(category).subscribe((res) => {
        this.toast.success(`${category.name}, resgistrada correctamente`);
        this.dialogRef.close(res)
      })
    }

  }
}
