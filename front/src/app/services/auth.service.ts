import { inject, Injectable } from '@angular/core';

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
  constructor() { }

  login(user: User): Observable<User> {
    return this.http.post<User>(`${this.urlEndPoint}/token/`, user).pipe(
      tap((res: any) => {
        console.log('res', res);
        localStorage.setItem('token', res.access);
        this.router.navigate(['/admin']);
      })
    );
  }

  /** Load token from localstorage */
  getToken() {
    const token: string = localStorage.getItem('token') || '';
    if (token != '') {
      return token;
    } else {
      return null;
    }
  }

  logout() {
    localStorage.clear();
    this.router.navigate(['/auth/login'])
  }
}
