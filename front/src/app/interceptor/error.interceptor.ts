import { HttpErrorResponse, HttpEvent, HttpHandlerFn, HttpRequest } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { HotToastService } from '@ngxpert/hot-toast';
import { catchError, Observable, throwError } from 'rxjs';


export function errorInterceptor(
  req: HttpRequest<unknown>,
  next: HttpHandlerFn
): Observable<HttpEvent<unknown>> {
  const toast = inject(HotToastService);
  const router = inject(Router);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      let errorMessage = 'Ha ocurrido un error inesperado';

      // 1. Extraer el mensaje real de Django
      if (error.error && typeof error.error === 'object') {
        // Django DRF suele enviar { "detail": "..." } o { "error": "..." }
        errorMessage = error.error.detail || error.error.message || errorMessage;
      }

      switch (error.status) {
        case 401:
          console.warn('Sesión expirada o inválida. Limpiando...');
          localStorage.removeItem('token');
          router.navigate(['/auth/login']);
          toast.error('Sesión expirada. Por favor, inicia sesión de nuevo.');
          break;

        case 403:
          toast.error('No tienes permisos para realizar esta acción.');
          localStorage.removeItem('token')
          router.navigate(['/auth/login'])
          break;

        case 400:
          // Útil para errores de validación que no manejaste en el componente
          toast.warning('Datos inválidos. Revisa la información.');
          break;

        case 500:
          toast.error('Error interno del servidor. Inténtalo más tarde.');
          break;

        default:
          toast.error(errorMessage);
          break;
      }

      return throwError(() => error);
    })
  );
}
