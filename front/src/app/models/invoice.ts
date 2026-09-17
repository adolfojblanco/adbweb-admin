export enum InvoiceDocumentType {
  QUOTE = 'QUOTE',
  INVOICE = 'INVOICE',
}

export enum InvoiceStatus {
  DRAFT = 'DRAFT',
  ISSUED = 'ISSUED',
  ACCEPTED = 'ACCEPTED',
  PAID = 'PAID',
  CANCELLED = 'CANCELLED',
}

export interface InvoiceItem {
  id: number;
  product?: number | null;
  product_name?: string;
  quantity: number;
  unit_price: number;
  discount: number;
  subtotal: number;
}

export interface Invoice {
  id: number;
  customer?: number;
  number: string;
  document_type: InvoiceDocumentType;
  customer_name: string;
  customer_tax_id: string;
  issue_date: string;
  due_date?: string | null;
  status: InvoiceStatus;
  subtotal: number;
  tax_amount: number;
  total: number;
  notes?: string;
  items: InvoiceItem[];
}
