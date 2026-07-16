export interface Company {
  id?: number;
  name: string;
  email_company: string;
  phone: string;
  website?: string | null;
  address?: string | null;
  city: string;
  state: string;
  postal_code?: string | null;
  logo?: string | null;
}
