import { inject, Injectable } from '@angular/core';
import { environment } from '../../environments/environment'
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Client } from '../models/client';

@Injectable({
  providedIn: 'root',
})
export class ClientsService {
  private readonly urlEndPoint: string = `${environment.apiAuth}/auth/customers`;
  private http = inject(HttpClient);

  loadCustomers(): Observable<Client[]> {
    return this.http.get<Client[]>(`${this.urlEndPoint}/`);
  }

  getById(id: number): Observable<Client> {
    return this.http.get<Client>(`${this.urlEndPoint}/${id}/`);
  }

  createCustomer(customer: Client): Observable<Client> {
    return this.http.post<Client>(`${this.urlEndPoint}/`, customer);
  }

  updateCustomer(id: number, customer: Client): Observable<Client> {
    return this.http.put<Client>(`${this.urlEndPoint}/${id}/`, customer);
  }

  deleteCustomer(id: number): Observable<void> {
    return this.http.delete<void>(`${this.urlEndPoint}/${id}/`);
  }
}
