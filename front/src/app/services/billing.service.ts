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

  taxTotal(items: InvoiceLineItem[], taxRate?: number): number {
    if (taxRate !== undefined && taxRate !== null) {
      return (this.subtotal(items) * taxRate) / 100;
    }
    return items.reduce((total, item) => {
      const itemRate = item.tax?.percentage ?? 0;
      return total + (this.lineSubtotal(item) * itemRate) / 100;
    }, 0);
  }

  total(items: InvoiceLineItem[], taxRate?: number): number {
    return this.subtotal(items) + this.taxTotal(items, taxRate);
  }
}
