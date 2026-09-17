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

  createQuote(
    customer: Client,
    items: InvoiceLineItem[],
    taxId: number,
    notes?: string,
    dueDate?: string | null,
  ): Observable<Invoice> {
    return this.http.post<Invoice>(`${this.urlEndPoint}/`, this.buildPayload(customer, items, taxId, notes, dueDate));
  }

  updateQuote(
    id: number,
    customer: Client,
    items: InvoiceLineItem[],
    taxId: number,
    notes?: string,
    dueDate?: string | null,
  ): Observable<Invoice> {
    return this.http.patch<Invoice>(`${this.urlEndPoint}/${id}/`, this.buildPayload(customer, items, taxId, notes, dueDate));
  }

  issue(id: number): Observable<Invoice> {
    return this.http.post<Invoice>(`${this.urlEndPoint}/${id}/issue/`, {});
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

  private buildPayload(
    customer: Client,
    items: InvoiceLineItem[],
    taxId: number,
    notes?: string,
    dueDate?: string | null,
  ) {
    return {
      customer: customer.id,
      document_type: 'QUOTE',
      tax: taxId,
      notes: notes ?? '',
      due_date: dueDate ?? null,
      items: items.map((item) => ({
        product: item.id,
        quantity: item.quantity,
        unit_price: item.sale_price,
        discount: 0,
      })),
    };
  }
}
