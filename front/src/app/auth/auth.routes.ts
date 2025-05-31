import { Routes } from '@angular/router';
import { LoginComponent } from './login/login.component';

export const authRoutes: Routes = [
  {
    path: 'auth',
    component: LoginComponent
  },
  {
    path: '**',
    redirectTo: 'auth'
  }
];

export default authRoutes;