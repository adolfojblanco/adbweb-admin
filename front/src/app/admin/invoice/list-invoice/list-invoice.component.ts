import { Component, inject, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { MaterialModule } from '../../shared/material/material.module';
import { InvoicesService } from '../../../services/invoices.service';
import { Invoice, InvoiceDocumentType, InvoiceStatus } from '../../../models/invoice';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-list-invoice',
  imports: [MaterialModule, RouterLink],
  templateUrl: './list-invoice.component.html',
  styles: ``,
})
export class ListInvoiceComponent implements OnInit {
  private invoicesService = inject(InvoicesService);
  private snackBar = inject(MatSnackBar);

  invoices = signal<Invoice[]>([]);
  displayedColumns: string[] = ['number', 'document_type', 'customer_name', 'issue_date', 'status', 'total', 'actions'];

  readonly statusLabels: Record<InvoiceStatus, string> = {
    [InvoiceStatus.DRAFT]: 'Borrador',
    [InvoiceStatus.ISSUED]: 'Emitida',
    [InvoiceStatus.ACCEPTED]: 'Aceptada',
    [InvoiceStatus.PAID]: 'Pagada',
    [InvoiceStatus.CANCELLED]: 'Cancelada',
  };

  readonly statusClasses: Record<InvoiceStatus, string> = {
    [InvoiceStatus.DRAFT]: 'bg-secondary',
    [InvoiceStatus.ISSUED]: 'bg-primary',
    [InvoiceStatus.ACCEPTED]: 'bg-info',
    [InvoiceStatus.PAID]: 'bg-success',
    [InvoiceStatus.CANCELLED]: 'bg-danger',
  };

  readonly documentTypeLabels: Record<InvoiceDocumentType, string> = {
    [InvoiceDocumentType.QUOTE]: 'Presupuesto',
    [InvoiceDocumentType.INVOICE]: 'Factura',
  };

  statusLabel(status: string): string {
    return this.statusLabels[status as InvoiceStatus] ?? status;
  }

  statusClass(status: string): string {
    return this.statusClasses[status as InvoiceStatus] ?? 'bg-secondary';
  }

  documentTypeLabel(type: string): string {
    return this.documentTypeLabels[type as InvoiceDocumentType] ?? type;
  }

  isQuote(invoice: Invoice): boolean {
    return invoice.document_type === InvoiceDocumentType.QUOTE;
  }

  ngOnInit() {
    this.loadInvoices();
  }

  loadInvoices() {
    this.invoicesService.getAll().subscribe((res) => {
      this.invoices.set(res);
    });
  }

  presentInvoice(invoice: Invoice) {
    this.invoicesService.issue(invoice.id).subscribe({
      next: (updated) => {
        this.invoices.update((list) =>
          list.map((item) => (item.id === updated.id ? updated : item)),
        );
        this.snackBar.open(`Documento ${updated.number} emitido como factura.`, 'Cerrar', {
          duration: 3000,
        });
      },
      error: () => {
        this.snackBar.open('No se pudo emitir el documento.', 'Cerrar', { duration: 3000 });
      },
    });
  }
}
