import { inject, Injectable, signal } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Category } from '../models/category';

@Injectable({
  providedIn: 'root'
})
export class CategoriesService {
  private readonly urlEndPoint: string = `${environment.apiUrl}/catalog/categories/`;
  private http = inject(HttpClient);


  loadCategories() {
    return this.http.get<Category[]>(`${this.urlEndPoint}`);
  }

}
