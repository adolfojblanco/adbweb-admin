import { inject, Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs';
import { Tax } from '../models/tax';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root',
})
export class TaxService {
  private readonly urlEndPoint: string = `${environment.apiUrl}/taxes`;
  private http = inject(HttpClient);


  /** Load active tax */
  loadActiveTax(): Observable<Tax[]> {
    return this.http.get<Tax[]>(`${this.urlEndPoint}/`)
  }

}
