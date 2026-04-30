import { HotToastService } from '@ngxpert/hot-toast';
import { computed, inject, Injectable, signal } from '@angular/core';

import { catchError, Observable, pipe, tap, throwError } from 'rxjs';
import { User } from '../models/user';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly urlEndPoint: string = `${environment.apiAuth}/auth`;
  private http = inject(HttpClient);
  private router = inject(Router);
  private toast = inject(HotToastService);

  // For auth
  private userSignal = signal<User | null>(null);
  public currentUser = computed(() => this.userSignal());
  private _token = signal<string | null>(localStorage.getItem('token'));
  public token = computed(() => this._token());



  login(user: User): Observable<any> {
    return this.http.post<any>(`${this.urlEndPoint}/token/`, user).pipe(
      tap((res) => {
        // SimpleJWT usa 'access'
        this._token.set(res.access);
        localStorage.setItem('token', res.access);
        this.router.navigate(['/admin']);
      }),
      catchError((err) => {
        const msg = err.error?.message || 'Error al iniciar sesión';
        this.toast.error(msg);
        return throwError(() => err);
      })
    );
  }

  // Get auth user
  getAuthUser(): Observable<User> {
    return this.http.get<User>(`${this.urlEndPoint}/me/`).pipe(
      tap((user) => {
        this.userSignal.set(user);
      })
    );
  }

  logout() {
    this.toast.success(`Sesión cerrada con exito`);
    localStorage.removeItem('token');
    this._token.set(null);
    this.userSignal.set(null);
    this.router.navigate(['/auth/login']);
  }
}
