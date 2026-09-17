import { ProductsService } from './../../../services/products.service';
import { Component, computed, inject, OnDestroy, OnInit, signal } from '@angular/core';
import { AuthService } from '../../../services/auth.service';
import { MaterialModule } from '../../shared/material/material.module';
import { Product } from '../../../models/product';
import { MatAutocompleteSelectedEvent } from '@angular/material/autocomplete';
import { BillingService, InvoiceLineItem } from '../../../services/billing.service';
import { Client } from '../../../models/client';
import { RouterLink } from '@angular/router';
import { Router } from '@angular/router';
import { InvoicesService } from '../../../services/invoices.service';
import { TaxesService } from '../../../services/taxes.service';
import { Tax } from '../../../models/tax';
import { HotToastService } from '@ngxpert/hot-toast';
import { FormsModule } from '@angular/forms';
import { Subject, Subscription } from 'rxjs';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';

@Component({
  selector: 'app-new-invoice',
  imports: [MaterialModule, RouterLink, FormsModule],
  templateUrl: './new-invoice.component.html',
  styles: ``,
})
export class NewInvoiceComponent implements OnInit, OnDestroy {
  authService = inject(AuthService);
  productService = inject(ProductsService);
  billingService = inject(BillingService);
  invoicesService = inject(InvoicesService);
  taxesService = inject(TaxesService);
  router = inject(Router);
  toast = inject(HotToastService);
  private searchInput$ = new Subject<string>();
  private searchSub?: Subscription;
  customers = signal<Client[]>([]);
  showDropdown = signal(false);
  searchInput = signal<string>('');
  products = signal<Product[]>([]);
  selectedCustomer = signal<Client | null>(null);
  invoiceProduct = signal<InvoiceLineItem[]>([]);
  taxes = signal<Tax[]>([]);
  selectedTaxId = signal<number | null>(null);
  dueDate = signal<string | null>(null);
  selectedTaxRate = computed(() => {
    const id = this.selectedTaxId();
    if (id == null) return 0;
    return this.taxes().find((t) => t.id === id)?.percentage ?? 0;
  });
  subtotal = computed(() => this.billingService.subtotal(this.invoiceProduct()));
  taxTotal = computed(() => this.billingService.taxTotal(this.invoiceProduct(), this.selectedTaxRate()));
  total = computed(() => this.billingService.total(this.invoiceProduct(), this.selectedTaxRate()));
  canSave = computed(
    () => !!this.selectedCustomer() && this.invoiceProduct().length > 0 && this.selectedTaxId() !== null,
  );


  ngOnInit() {
    this.taxesService.getAll().subscribe({
      next: (res) => {
        this.taxes.set(res);
        const firstTax = res[0];
        if (firstTax && firstTax.id != null) {
          this.selectedTaxId.set(firstTax.id);
        }
      },
      error: () => this.toast.error('No se pudieron cargar los impuestos.'),
    });

    this.loadAllProducts();

    this.searchSub = this.searchInput$
      .pipe(debounceTime(250), distinctUntilChanged())
      .subscribe((term) => this.runProductSearch(term));
  }

  ngOnDestroy(): void {
    this.searchSub?.unsubscribe();
  }

  onSearch(query: string) {
    this.searchInput$.next(query ?? '');
  }

  private loadAllProducts() {
    this.productService.searchProducts('').subscribe({
      next: (res) => this.products.set(res ?? []),
      error: () => this.products.set([]),
    });
  }

  private runProductSearch(query: string) {
    const term = query.trim();
    if (!term) {
      this.loadAllProducts();
      return;
    }
    this.productService.searchProducts(term).subscribe({
      next: (res) => this.products.set(res ?? []),
      error: () => this.products.set([]),
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

  displayProduct = (product: Product | null | undefined): string => {
    if (!product) return '';
    return product.sku ? `${product.sku} — ${product.name}` : product.name ?? '';
  };

  taxLabel(tax: Tax) {
    return `${tax.name} (${tax.percentage}%)`;
  }

  saveInvoice() {
    if (!this.canSave()) {
      this.toast.warning('Selecciona un cliente, un impuesto y añade al menos un producto.');
      return;
    }

    const customer = this.selectedCustomer()!;
    const items = this.invoiceProduct();
    const taxId = this.selectedTaxId()!;

    this.invoicesService.createQuote(customer, items, taxId, undefined, this.dueDate()).subscribe({
      next: (invoice) => {
        this.toast.success('Presupuesto guardado correctamente');
        this.router.navigate(['/admin/invoice/detailinvoice', invoice.id]);
      },
      error: (err) => {
        const detail = err?.error?.detail || err?.error || 'No se pudo guardar el presupuesto.';
        this.toast.error(typeof detail === 'string' ? detail : 'No se pudo guardar el presupuesto.');
      },
    });
  }

}
