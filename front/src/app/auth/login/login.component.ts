import { Component, inject, signal } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { HotToastService } from '@ngxpert/hot-toast';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule],
  templateUrl: './login.component.html',
  styles: ``
})
export class LoginComponent {
  private authService = inject(AuthService);
  private toas = inject(HotToastService);
  private fb = inject(FormBuilder);
  private hasError = signal(false);

  constructor(private toast: HotToastService) { }


  public loginForm: FormGroup = this.fb.group({
    username: ['', [Validators.required, Validators.minLength(3)]],
    password: ['', [Validators.required]],
  });

  login() {
    if (this.loginForm.invalid) {
      this.hasError.set(true);
      this.toast.error("Verifica el formulario, datos invalidos.")
      return;
    }
    const { username = '', password = '' } = this.loginForm.value
  }


}
