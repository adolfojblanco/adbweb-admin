import { inject, Injectable } from '@angular/core';
import { environment } from '../../environments/environment'
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root',
})
export class ClientsService {
  private readonly urlEndPoint: string = `${environment.apiUrl}/clients`;
  private http = inject(HttpClient);



}
