import { ProductsService } from './../../../services/products.service';
import { Component, inject, input, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../../services/auth.service';
import { MaterialModule } from '../../shared/material/material.module';
import { Product } from '../../../models/product';
import { MatAutocompleteSelectedEvent } from '@angular/material/autocomplete';
import { preserveWhitespacesDefault } from '@angular/compiler';
import { findInputsOnElementWithAttr } from '@angular/cdk/schematics';

@Component({
  selector: 'app-new-invoice',
  imports: [FormsModule, MaterialModule],
  templateUrl: './new-invoice.component.html',
  styles: ``,
})
export class NewInvoiceComponent implements OnInit {
  authService = inject(AuthService);
  productService = inject(ProductsService)
  customers = signal<any[]>([]);
  showDropdown = signal(false);
  searchInput = signal<string>('');
  products = signal<Product[]>([]);
  invoiceProduct = signal<Product[]>([]);


  ngOnInit() {

  }


  onSearch(query: string) {
    if(!query.trim()) return; // si esta vacio no buscamos
    this.productService.searchProducts(query).subscribe((res) => {
      this.products.set(res)
    })
  }

  selectedProduct(event: MatAutocompleteSelectedEvent, inputElement: HTMLInputElement) {
    const product = event.option.value;
    this.invoiceProduct.update((prev) => [...prev, product])
    inputElement.value = '';
    this.products.set([]);
    inputElement.focus();
  }

  loadProducts() {
    this.productService.loadProducts().subscribe((res) =>  {
      this.products.set(res)
      console.log(this.products());
    })
  }

  searchCutomer() {
    const search = this.searchInput().trim();
    this.authService.customerSearch(search).subscribe((res) => {
      this.customers.set(res);
      console.log(res);
      this.showDropdown.set(true);
    })
  }

}
