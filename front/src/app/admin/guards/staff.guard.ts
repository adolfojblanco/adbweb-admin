import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';
import { catchError, map, of, take } from 'rxjs';
import { AuthService } from '../../services/auth.service';
import { HotToastService } from '@ngxpert/hot-toast';

export const staffGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);
  const toast = inject(HotToastService);

  const user = authService.currentUser();
  if (user?.is_staff) {
    return true;
  }

  return authService.getAuthUser().pipe(
    take(1),
    map((loaded) => {
      if (loaded?.is_staff) {
        return true;
      }
      toast.error('No tienes permisos para acceder a esta sección.');
      router.navigate(['/admin']);
      return false;
    }),
    catchError(() => {
      router.navigate(['/admin']);
      return of(false);
    }),
  );
};
