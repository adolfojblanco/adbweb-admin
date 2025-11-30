import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from './auth.service';



export const authInterceptor: HttpInterceptorFn = (req, next) => {

  const router = inject(Router);
  const authServices = inject(AuthService);
  const token = authServices.getToken();

  if (authServices.getToken()) {
    req = req.clone({
      setHeaders: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
    })
  }

  return next(req);
};
