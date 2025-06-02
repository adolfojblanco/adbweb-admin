export interface User {
  id?: number;
  first_name: string;
  last_name: string;
  username: string;
  password: string;
  role: string;
  is_active: boolean;
  is_staff: boolean;
  access_token?: string;
  token?: string;

}
