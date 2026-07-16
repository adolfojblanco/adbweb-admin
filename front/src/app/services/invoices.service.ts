import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Invoice } from '../models/invoice';
import { Client } from '../models/client';
import { InvoiceLineItem } from './billing.service';

@Injectable({
  providedIn: 'root',
})
export class InvoicesService {
  private readonly urlEndPoint = `${environment.apiUrl.replace(/\/$/, '')}/invoices`;
  private http = inject(HttpClient);

  getAll(): Observable<Invoice[]> {
    return this.http.get<Invoice[]>(`${this.urlEndPoint}/`);
  }

  getById(id: number): Observable<Invoice> {
    return this.http.get<Invoice>(`${this.urlEndPoint}/${id}/`);
  }

  createBudget(customer: Client, items: InvoiceLineItem[], totals: { subtotal: number; taxTotal: number; total: number }, notes?: string): Observable<Invoice> {
    return this.http.post<Invoice>(`${this.urlEndPoint}/`, this.buildPayload(customer, items, notes));
  }

  updateBudget(id: number, customer: Client, items: InvoiceLineItem[], totals: { subtotal: number; taxTotal: number; total: number }, notes?: string): Observable<Invoice> {
    return this.http.patch<Invoice>(`${this.urlEndPoint}/${id}/`, this.buildPayload(customer, items, notes));
  }

  setStatus(id: number, newStatus: string): Observable<Invoice> {
    return this.http.post<Invoice>(`${this.urlEndPoint}/${id}/set-status/`, { status: newStatus });
  }

  sendEmail(id: number): Observable<{ detail: string }> {
    return this.http.post<{ detail: string }>(`${this.urlEndPoint}/${id}/send-email/`, {});
  }

  downloadPdf(id: number): Observable<Blob> {
    return this.http.get(`${this.urlEndPoint}/${id}/pdf/`, { responseType: 'blob' });
  }

  private buildPayload(customer: Client, items: InvoiceLineItem[], notes?: string) {
    return {
      customer: customer.id,
      notes: notes ?? '',
      lines: items.map((item) => ({
        product: item.id,
        description: item.name,
        quantity: item.quantity,
        unit_price: item.sale_price,
        tax_percentage: item.tax?.percentage ?? 0,
      })),
    };
  }
}
