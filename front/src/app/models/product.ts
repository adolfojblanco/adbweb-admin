import { Category } from "./category";

export interface Product {
  id?: number;
  sku: string;
  name: string;
  description: string
  active: boolean;
  unit_price: number;
  tax: number;
  category: Category
}
