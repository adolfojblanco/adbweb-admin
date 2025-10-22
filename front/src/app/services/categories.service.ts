import { inject, Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class CategoriesService {
  private readonly urlEndPoint: string = `${environment.apiUrl}/categories/`;
  private http = inject(HttpClient);


  loadCategories() {
    return this.http.get(`${this.urlEndPoint}`);
  }

}
