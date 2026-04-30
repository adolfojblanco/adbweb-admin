import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs';
import { Product } from '../models/product';

@Injectable({
  providedIn: 'root',
})
export class ProductsService {

  private readonly urlEndPoint: string = `${environment.apiUrl}/products`;
  private http = inject(HttpClient);


  loadProducts(): Observable<Product[]> {
    return this.http.get<Product[]>(`${this.urlEndPoint}/`);
  }

  newProduct(product: Product) {
    return this.http.post<Product>(`${this.urlEndPoint}/`, product)
  }

  editProduct(product: Product): Observable<Product> {
    return this.http.put<Product>(`${this.urlEndPoint}/${product.id}/`, product)
  }

}
