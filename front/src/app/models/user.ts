import { Customer } from './customer';
import { Role } from './role.enum';

export interface User {
  id: number;

  username: string;
  email: string;

  first_name: string;
  last_name: string;

  role: Role;

  customer?: Customer | null;

  is_admin?: boolean;
  is_seller?: boolean;
  is_client?: boolean;
}
