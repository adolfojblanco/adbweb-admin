import { Category } from "./category";
import { Tax } from "./tax";

export interface Product {
  id?: number;
  sku: string;
  name: string;
  description: string
  is_active: boolean;
  slug?: string
  sale_price: number;
  cost_price: number;
  tax: Tax;
  category: Category
}
