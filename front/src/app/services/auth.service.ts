import { computed, inject, Injectable, signal } from '@angular/core';

import { catchError, Observable, pipe, tap } from 'rxjs';
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

  // Inicializamos con el valor real del localStorage
  private _token = signal<string | null>(localStorage.getItem('token'));
  public token = this._token.asReadonly(); // Mejor práctica que computed para este caso

  login(user: User): Observable<any> {
    return this.http.post<any>(`${this.urlEndPoint}/token/`, user).pipe(
      tap((res) => {
        const accessToken = res.access; // SimpleJWT usa 'access'

        // 1. Guardamos en el Signal
        this._token.set(accessToken);

        // 2. Guardamos en LocalStorage
        localStorage.setItem('token', accessToken);

        this.router.navigate(['/admin']);
      })
    );
  }

  logout() {
    localStorage.removeItem('token');
    this._token.set(null); // Limpiamos el signal
    this.router.navigate(['/auth/login']);
  }
}
