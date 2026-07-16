import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { HotToastService } from '@ngxpert/hot-toast';
import { MatAutocompleteSelectedEvent } from '@angular/material/autocomplete';

import { MaterialModule } from '../../shared/material/material.module';
import { ProductsService } from '../../../services/products.service';
import { AuthService } from '../../../services/auth.service';
import { BillingService, InvoiceLineItem } from '../../../services/billing.service';
import { InvoicesService } from '../../../services/invoices.service';
import { Product } from '../../../models/product';
import { Client } from '../../../models/client';

@Component({
  selector: 'app-edit-invoice',
  imports: [MaterialModule, RouterLink],
  templateUrl: './edit-invoice.component.html',
  styles: ``,
})
export class EditInvoiceComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private toast = inject(HotToastService);
  private authService = inject(AuthService);
  private productService = inject(ProductsService);
  billingService = inject(BillingService);
  private invoicesService = inject(InvoicesService);

  invoiceId = signal<number | null>(null);
  customers = signal<Client[]>([]);
  showDropdown = signal(false);
  searchInput = signal<string>('');
  products = signal<Product[]>([]);
  selectedCustomer = signal<Client | null>(null);
  invoiceProduct = signal<InvoiceLineItem[]>([]);
  notes = signal<string>('');
  subtotal = computed(() => this.billingService.subtotal(this.invoiceProduct()));
  taxTotal = computed(() => this.billingService.taxTotal(this.invoiceProduct()));
  total = computed(() => this.billingService.total(this.invoiceProduct()));
  canSave = computed(() => !!this.selectedCustomer() && this.invoiceProduct().length > 0);

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (!Number.isNaN(id)) {
      this.invoiceId.set(id);
      this.loadInvoice(id);
    }
  }

  loadInvoice(id: number) {
    this.invoicesService.getById(id).subscribe((invoice) => {
      this.selectedCustomer.set({
        id: invoice.customer,
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
      this.notes.set(invoice.notes ?? '');
      this.invoiceProduct.set(
        invoice.lines.map((line) => ({
          id: line.product ?? line.id,
          sku: '',
          name: line.product_name || line.description,
          description: line.description,
          is_active: true,
          sale_price: line.unit_price,
          cost_price: 0,
          tax: { name: 'IVA', percentage: line.tax_percentage, is_active: true },
          category: { name: '', is_active: true },
          quantity: line.quantity,
        })),
      );
    });
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
    if (!this.canSave() || !invoiceId) {
      this.toast.warning('Selecciona un cliente y añade al menos un producto.');
      return;
    }

    const customer = this.selectedCustomer()!;
    const items = this.invoiceProduct();

    this.invoicesService.updateBudget(invoiceId, customer, items, {
      subtotal: this.subtotal(),
      taxTotal: this.taxTotal(),
      total: this.total(),
    }, this.notes()).subscribe((invoice) => {
      this.toast.success('Presupuesto actualizado correctamente');
      this.router.navigate(['/admin/invoice/detailinvoice', invoice.id]);
    });
  }
}
