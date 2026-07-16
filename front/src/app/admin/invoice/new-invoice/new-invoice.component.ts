import { ProductsService } from './../../../services/products.service';
import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { AuthService } from '../../../services/auth.service';
import { MaterialModule } from '../../shared/material/material.module';
import { Product } from '../../../models/product';
import { MatAutocompleteSelectedEvent } from '@angular/material/autocomplete';
import { BillingService, InvoiceLineItem } from '../../../services/billing.service';
import { Client } from '../../../models/client';
import { RouterLink } from '@angular/router';
import { Router } from '@angular/router';
import { InvoicesService } from '../../../services/invoices.service';
import { HotToastService } from '@ngxpert/hot-toast';

@Component({
  selector: 'app-new-invoice',
  imports: [MaterialModule, RouterLink],
  templateUrl: './new-invoice.component.html',
  styles: ``,
})
export class NewInvoiceComponent implements OnInit {
  authService = inject(AuthService);
  productService = inject(ProductsService);
  billingService = inject(BillingService);
  invoicesService = inject(InvoicesService);
  router = inject(Router);
  toast = inject(HotToastService);
  customers = signal<Client[]>([]);
  showDropdown = signal(false);
  searchInput = signal<string>('');
  products = signal<Product[]>([]);
  selectedCustomer = signal<Client | null>(null);
  invoiceProduct = signal<InvoiceLineItem[]>([]);
  subtotal = computed(() => this.billingService.subtotal(this.invoiceProduct()));
  taxTotal = computed(() => this.billingService.taxTotal(this.invoiceProduct()));
  total = computed(() => this.billingService.total(this.invoiceProduct()));
  canSave = computed(() => !!this.selectedCustomer() && this.invoiceProduct().length > 0);


  ngOnInit() {

  }

  onSearch(query: string) {
    if (!query.trim()) {
      this.products.set([]);
      return;
    }
    this.productService.searchProducts(query).subscribe((res) => {
      this.products.set(res);
    });
  }

  selectedProduct(event: MatAutocompleteSelectedEvent, inputElement: HTMLInputElement) {
    const product = event.option.value as Product;
    this.invoiceProduct.update((prev) => {
      const existing = prev.find((item) => item.id === product.id);

      if (existing) {
        return prev.map((item) =>
          item.id === product.id ? { ...item, quantity: item.quantity + 1 } : item,
        );
      }

      return [...prev, { ...product, quantity: 1 }];
    });
    inputElement.value = '';
    this.products.set([]);
    inputElement.focus();
  }

  removeProduct(productId?: number) {
    this.invoiceProduct.update((prev) => prev.filter((item) => item.id !== productId));
  }

  updateQuantity(productId: number | undefined, quantity: number) {
    if (!productId || quantity < 1) return;

    this.invoiceProduct.update((prev) =>
      prev.map((item) => (item.id === productId ? { ...item, quantity } : item)),
    );
  }

  loadProducts() {
    this.productService.loadProducts().subscribe((res) => {
      this.products.set(res);
    });
  }

  searchCustomer(query: string) {
    if (!query.trim()) {
      this.customers.set([]);
      this.showDropdown.set(false);
      this.selectedCustomer.set(null);
      return;
    }

    this.searchInput.set(query);
    this.selectedCustomer.set(null);
    this.authService.customerSearch(query).subscribe((res) => {
      this.customers.set(res);
      this.showDropdown.set(true);
    });
  }

  searchCutomer(query: string) {
    this.searchCustomer(query);
  }

  selectCustomer(customer: Client) {
    this.selectedCustomer.set(customer);
    this.searchInput.set(customer.billing_name);
    this.customers.set([]);
    this.showDropdown.set(false);
  }

  customerLabel(customer: Client) {
    return customer.billing_name;
  }

  saveInvoice() {
    if (!this.canSave()) {
      this.toast.warning('Selecciona un cliente y añade al menos un producto.');
      return;
    }

    const customer = this.selectedCustomer()!;
    const items = this.invoiceProduct();
    const totals = {
      subtotal: this.subtotal(),
      taxTotal: this.taxTotal(),
      total: this.total(),
    };

    this.invoicesService.createBudget(customer, items, totals).subscribe((invoice) => {
      this.toast.success('Presupuesto guardado correctamente');
      this.router.navigate(['/admin/invoice/detailinvoice', invoice.id]);
    });
  }

}
