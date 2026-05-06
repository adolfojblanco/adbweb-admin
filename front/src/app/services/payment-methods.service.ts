import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs';
import { PaymentsMethods } from '../models/payments-methods';

@Injectable({
  providedIn: 'root',
})
export class PaymentMethodsService {
  private readonly urlEndPoint: string = `${environment.apiUrl}/payment-methods`;
  private http = inject(HttpClient)



  getAllPaymentMethods(): Observable<PaymentsMethods[]> {
    return this.http.get<PaymentsMethods[]>(`${this.urlEndPoint}/`)
  }


  newPaymentMethod(paymentMethod: PaymentsMethods): Observable<PaymentsMethods> {
    return this.http.post<PaymentsMethods>(`${this.urlEndPoint}/`, paymentMethod)
  }

  editPaymentMethod(paymentMethod: PaymentsMethods): Observable<PaymentsMethods> {
    return this.http.put<PaymentsMethods>(`${this.urlEndPoint}/${paymentMethod.id}/`, paymentMethod)
  }

}
