import { CustomerType } from './customer-type.enum';

export interface Customer {
  id: number;

  customer_type: CustomerType;

  billing_name: string;
  tax_id: string;

  address: string;
  city: string;
  province: string;
  postal_code?: string | null;
  country: string;

  contact_email: string;
  phone?: string | null;

  created_at: string;
  updated_at: string;
}
