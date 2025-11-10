import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from './auth.service';



export const authInterceptor: HttpInterceptorFn = (req, next) => {

  const router = inject(Router);
  const authServices = inject(AuthService);

  c


  return next(req);
};
