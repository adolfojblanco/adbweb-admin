import { Component, inject, signal } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { HotToastService } from '@ngxpert/hot-toast';
import { AuthService } from '../../services/auth.service';
import { MaterialModule } from '../../admin/shared/material/material.module';

@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule, MaterialModule],
  templateUrl: './login.component.html',
  styles: ``
})
export class LoginComponent {
  private authService = inject(AuthService);
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
    this.authService.login(this.loginForm.value).subscribe({
      next: (res) => {
        // 1. Éxito: El usuario entró
        const username = this.loginForm.get('username')?.value;
        this.toast.success(`Bienvenido, ${username}`);
        console.log('Login exitoso:', res);

        // Aquí normalmente navegarías al dashboard
        // this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        // 2. Error: Manejo de fallos (401, 403, 500, etc.

        // Si Django DRF devuelve un 401, el error suele venir en err.error
        const errorMsg = err.status === 401
          ? 'Credenciales inválidas'
          : 'Error de conexión con el servidor';

        this.toast.error(errorMsg);
      },

    });
  }
}
