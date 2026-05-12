import { Supplier } from './../models/suppliers';
import { inject, Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';


@Injectable({
  providedIn: 'root',
})
export class SuppliersService {
  private readonly urlEndPoint: string = `${environment.apiUrl}/suppliers`;
  private http = inject(HttpClient);

  /**
   * Get all supliers
   */
  getAllSuppliers(): Observable<[]> {
    return this.http.get<[]>(`${this.urlEndPoint}`)
  }

  // Create a supplier
  newSupplier(supplier: Supplier): Observable<Supplier> {
    return this.http.post<Supplier>(`${this.urlEndPoint}/`, supplier)
  }

  // Edit supplier
  editSupplier(supplier: Supplier): Observable<Supplier> {
    return this.http.put<Supplier>(`${this.urlEndPoint}/${supplier.id}/`, supplier);
  }

}
