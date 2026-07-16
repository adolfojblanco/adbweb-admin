import { Injectable } from '@angular/core';

import { Product } from '../models/product';

export interface InvoiceLineItem extends Product {
  quantity: number;
}

@Injectable({
  providedIn: 'root',
})
export class BillingService {
  lineSubtotal(item: InvoiceLineItem): number {
    return item.sale_price * item.quantity;
  }

  subtotal(items: InvoiceLineItem[]): number {
    return items.reduce((total, item) => total + this.lineSubtotal(item), 0);
  }

  taxTotal(items: InvoiceLineItem[]): number {
    return items.reduce((total, item) => {
      const taxRate = item.tax?.percentage ?? 0;
      return total + (this.lineSubtotal(item) * taxRate) / 100;
    }, 0);
  }

  total(items: InvoiceLineItem[]): number {
    return this.subtotal(items) + this.taxTotal(items);
  }
}
