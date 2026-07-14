import { inject, Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Category } from '../models/category';
import { observableToBeFn } from 'rxjs/internal/testing/TestScheduler';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class CategoriesService {
  private readonly urlEndPoint: string = `${environment.apiUrl}/categories`;
  private http = inject(HttpClient);


  loadCategories(): Observable<Category[]> {
    return this.http.get<Category[]>(`${this.urlEndPoint}/`);
  }

  loadActiveCategories(): Observable<Category[]> {
    return this.http.get<Category[]>(`${this.urlEndPoint}/active/`);
  }

  editCategory(category: Category) {
    return this.http.put<Category>(`${this.urlEndPoint}/${category.id}/`, category);
  }

  newCategory(category: Category): Observable<Category> {
    return this.http.post<Category>(`${this.urlEndPoint}/`, category)
  }

}
