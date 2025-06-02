import { inject, Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { Observable, tap } from 'rxjs';
import { User } from '../models/user';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly urlEndPoint: string = `${environment.apiUrl}/auth`;
  private http = inject(HttpClient);
  private router = inject(Router);
  constructor() { }

  login(user: User): Observable<User> {
    return this.http.post<User>(`${this.urlEndPoint}/token/`, user).pipe(
      tap((res: any) => {
        localStorage.setItem('token', res.access);
        this.router.navigate(['/admin']);
      })
    );
  }

  logout() {
    localStorage.clear();
    this.router.navigate(['/auth/login'])
  }
}
