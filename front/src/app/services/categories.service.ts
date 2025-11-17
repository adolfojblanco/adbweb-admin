import { inject, Injectable, signal } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Category } from '../models/category';
import { observableToBeFn } from 'rxjs/internal/testing/TestScheduler';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class CategoriesService {
  private readonly urlEndPoint: string = `${environment.apiUrl}/categories/`;
  private http = inject(HttpClient);


  loadCategories(): Observable<Category[]> {
    return this.http.get<Category[]>(`${this.urlEndPoint}`);
  }

  editCategory(category: Category) {
    return this.http.post<Category>(`${this.urlEndPoint}`, category)
  }

}
