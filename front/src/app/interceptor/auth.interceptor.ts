import { HttpHandlerFn, HttpInterceptorFn, HttpRequest } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth.service';



export function authInterceptor(
  req: HttpRequest<unknown>,
  next: HttpHandlerFn,
) {
  const authService = inject(AuthService);
  const token = authService.token();

  let headers = req.headers
    .set('Accept', 'application/json')

  if (token && token !== 'null' && token !== 'undefined') {
    headers = headers.set('Authorization', `Bearer ${token}`);
  }

  const newReq = req.clone({
    headers,
  });

  return next(newReq);
}
