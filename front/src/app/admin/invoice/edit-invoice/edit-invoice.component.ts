import { Component, computed, inject, OnDestroy, OnInit, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { HotToastService } from '@ngxpert/hot-toast';
import { MatAutocompleteSelectedEvent } from '@angular/material/autocomplete';

import { MaterialModule } from '../../shared/material/material.module';
import { ProductsService } from '../../../services/products.service';
import { AuthService } from '../../../services/auth.service';
import { BillingService, InvoiceLineItem } from '../../../services/billing.service';
import { InvoicesService } from '../../../services/invoices.service';
import { TaxesService } from '../../../services/taxes.service';
import { Product } from '../../../models/product';
import { Client } from '../../../models/client';
import { Tax } from '../../../models/tax';
import { FormsModule } from '@angular/forms';
import { Subject, Subscription } from 'rxjs';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';

@Component({
  selector: 'app-edit-invoice',
  imports: [MaterialModule, RouterLink, FormsModule],
  templateUrl: './edit-invoice.component.html',
  styles: ``,
})
export class EditInvoiceComponent implements OnInit, OnDestroy {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private toast = inject(HotToastService);
  private authService = inject(AuthService);
  private productService = inject(ProductsService);
  billingService = inject(BillingService);
  private invoicesService = inject(InvoicesService);
  private taxesService = inject(TaxesService);
  private searchInput$ = new Subject<string>();
  private searchSub?: Subscription;

  invoiceId = signal<number | null>(null);
  invoiceNumber = signal<string>('');
  customers = signal<Client[]>([]);
  showDropdown = signal(false);
  searchInput = signal<string>('');
  products = signal<Product[]>([]);
  selectedCustomer = signal<Client | null>(null);
  invoiceProduct = signal<InvoiceLineItem[]>([]);
  notes = signal<string>('');
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

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (!Number.isNaN(id)) {
      this.invoiceId.set(id);
      this.loadTaxes();
      this.loadInvoice(id);
    }

    this.searchSub = this.searchInput$
      .pipe(debounceTime(250), distinctUntilChanged())
      .subscribe((term) => this.runProductSearch(term));

    this.loadAllProducts();
  }

  ngOnDestroy(): void {
    this.searchSub?.unsubscribe();
  }

  loadTaxes() {
    this.taxesService.getAll().subscribe({
      next: (res) => this.taxes.set(res),
      error: () => this.toast.error('No se pudieron cargar los impuestos.'),
    });
  }

  taxLabel(tax: Tax) {
    return `${tax.name} (${tax.percentage}%)`;
  }

  loadInvoice(id: number) {
    this.invoicesService.getById(id).subscribe({
      next: (invoice) => {
        this.invoiceNumber.set(invoice.number);
        this.notes.set(invoice.notes ?? '');
        this.dueDate.set(invoice.due_date ?? null);
        this.selectedTaxId.set(null);
        this.selectedCustomer.set({
          id: invoice.customer ?? 0,
          customer_type: 'COMPANY',
          billing_name: invoice.customer_name,
          tax_id: invoice.customer_tax_id,
          address: '',
          city: '',
          province: '',
          postal_code: null,
          contact_email: '',
          phone: null,
          user: null,
        });
        this.searchInput.set(invoice.customer_name);
        this.invoiceProduct.set(
          invoice.items.map((item) => ({
            id: item.product ?? item.id,
            sku: '',
            name: item.product_name || '',
            description: '',
            is_active: true,
            sale_price: item.unit_price,
            cost_price: 0,
            tax: { name: 'IVA', percentage: 0, is_active: true },
            category: { name: '', is_active: true },
            quantity: item.quantity,
          })),
        );

        const firstTax = this.taxes()[0];
        if (firstTax && firstTax.id != null) {
          this.selectedTaxId.set(firstTax.id);
        }
      },
      error: () => this.toast.error('No se pudo cargar el presupuesto.'),
    });
  }

  onSearch(query: string) {
    this.searchInput$.next(query ?? '');
  }

  displayProduct = (product: Product | null | undefined): string => {
    if (!product) return '';
    return product.sku ? `${product.sku} — ${product.name}` : product.name ?? '';
  };

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
        return prev.map((item) => item.id === product.id ? { ...item, quantity: item.quantity + 1 } : item);
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
    this.invoiceProduct.update((prev) => prev.map((item) => item.id === productId ? { ...item, quantity } : item));
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
    const invoiceId = this.invoiceId();
    if (!this.canSave() || !invoiceId || this.selectedTaxId() == null) {
      this.toast.warning('Selecciona un cliente, un impuesto y añade al menos un producto.');
      return;
    }

    const customer = this.selectedCustomer()!;
    const items = this.invoiceProduct();
    const taxId = this.selectedTaxId()!;

    this.invoicesService.updateQuote(invoiceId, customer, items, taxId, this.notes(), this.dueDate()).subscribe({
      next: (invoice) => {
        this.toast.success('Presupuesto actualizado correctamente');
        this.router.navigate(['/admin/invoice/detailinvoice', invoice.id]);
      },
      error: () => this.toast.error('No se pudo actualizar el presupuesto.'),
    });
  }
}
