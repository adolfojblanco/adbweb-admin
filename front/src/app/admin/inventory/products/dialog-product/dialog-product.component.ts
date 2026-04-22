import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { Component, inject, OnInit } from '@angular/core';
import { MaterialModule } from '../../../shared/material/material.module';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators, ɵInternalFormsSharedModule } from '@angular/forms';
import { C } from '@angular/cdk/keycodes';

@Component({
  selector: 'app-dialog-product',
  imports: [MaterialModule, ReactiveFormsModule],
  templateUrl: './dialog-product.component.html',
  styles: ``,
})
export class DialogProductComponent implements OnInit {
  private fb = inject(FormBuilder);
  private data = inject(MAT_DIALOG_DATA);


  constructor(public MatDialogRef: MatDialogRef<DialogProductComponent>) { };

  ngOnInit() {
    if (this.data) {
      console.log(this.data);
      this.productForm.reset(this.data);
    }
  }



  public productForm: FormGroup = this.fb.group({
    id: [null],
    name: ['', [Validators.required, Validators.minLength(3)]],
    description: [],
    unit_price: [],
    category: [],
    active: [true]
  })







}
