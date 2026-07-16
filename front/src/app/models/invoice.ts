export enum InvoiceDocumentType {
  BUDGET = 'BUDGET',
  INVOICE = 'INVOICE',
}

export enum InvoiceStatus {
  DRAFT = 'DRAFT',
  ISSUED = 'ISSUED',
  PAID = 'PAID',
  CANCELLED = 'CANCELLED',
}

export interface InvoiceLine {
  id: number;
  product?: number | null;
  product_name?: string;
  description: string;
  quantity: number;
  unit_price: number;
  tax_percentage: number;
  line_subtotal: number;
  tax_amount: number;
  line_total: number;
}

export interface Invoice {
  id: number;
  customer?: number;
  invoice_number: string;
  document_type: InvoiceDocumentType;
  customer_name: string;
  customer_tax_id: string;
  issue_date: string;
  due_date?: string | null;
  status: InvoiceStatus;
  subtotal: number;
  tax_total: number;
  total: number;
  notes?: string;
  lines: InvoiceLine[];
}
