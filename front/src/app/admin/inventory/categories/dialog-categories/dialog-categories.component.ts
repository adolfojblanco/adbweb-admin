import { Component, inject } from '@angular/core';
import { MaterialModule } from '../../../shared/material/material.module';
import { HotToastService } from '@ngxpert/hot-toast';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';

@Component({
  selector: 'app-dialog-categories',
  imports: [MaterialModule, ReactiveFormsModule],
  templateUrl: './dialog-categories.component.html',
  styles: ``,
})
export class DialogCategoriesComponent {
  private fb = inject(FormBuilder);
  public toast = inject(HotToastService);
  constructor() {

  }

  public categoryForm: FormGroup = this.fb.group({
    name: ['', [Validators.required, Validators.minLength(3)]],
    active: [true]
  })

  submit() {
    if (this.categoryForm.invalid) {
      this.toast.error('Todos los campos son obligatorios');
      return;
    }

    console.log(this.categoryForm.value);

  }
}
