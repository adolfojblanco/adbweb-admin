import { User } from './user';

export enum CustomerType {
  PERSON = 'PERSON',
  COMPANY = 'COMPANY',
}

export interface Client {
  id?: number,
  customer_type: string,
  billing_name: string
  tax_id: string,
  address: string,
  city: string
  province: string
  postal_code?: string | null

  contact_email: string,
  phone?: string | null,
  user?: User | null,
}
