import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Tax } from '../models/tax';

@Injectable({
  providedIn: 'root',
})
export class TaxesService {
  private readonly urlEndPoint = `${environment.apiUrl.replace(/\/$/, '')}/taxes`;
  private http = inject(HttpClient);

  getAll(): Observable<Tax[]> {
    return this.http.get<Tax[]>(`${this.urlEndPoint}/`);
  }
}
