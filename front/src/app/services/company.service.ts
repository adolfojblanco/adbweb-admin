import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Company } from '../models/company';

@Injectable({
  providedIn: 'root',
})
export class CompanyService {
  private readonly urlEndPoint = `${environment.apiUrl}/company`;
  private http = inject(HttpClient);

  getCompany(): Observable<Company> {
    return this.http.get<Company>(`${this.urlEndPoint}/`);
  }

  updateCompany(formData: FormData): Observable<Company> {
    return this.http.patch<Company>(`${this.urlEndPoint}/`, formData);
  }
}
