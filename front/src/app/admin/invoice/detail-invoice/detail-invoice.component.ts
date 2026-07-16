import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MaterialModule } from '../../shared/material/material.module';
import { InvoicesService } from '../../../services/invoices.service';
import { Invoice } from '../../../models/invoice';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-detail-invoice',
  imports: [MaterialModule, RouterLink],
  templateUrl: './detail-invoice.component.html',
  styles: ``,
})
export class DetailInvoiceComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private invoicesService = inject(InvoicesService);
  private snackBar = inject(MatSnackBar);

  invoice = signal<Invoice | null>(null);
  isBudget = computed(() => this.invoice()?.document_type === 'BUDGET');
  sending = signal(false);

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (!Number.isNaN(id)) {
      this.invoicesService.getById(id).subscribe((res) => {
        this.invoice.set(res ?? null);
      });
    }
  }

  sendByEmail() {
    const current = this.invoice();
    if (!current) return;

    this.sending.set(true);
    this.invoicesService.sendEmail(current.id).subscribe({
      next: (res) => {
        this.sending.set(false);
        this.snackBar.open(res.detail || 'Email enviado.', 'Cerrar', { duration: 4000 });
      },
      error: (err) => {
        this.sending.set(false);
        const message = err?.error?.detail || 'No se pudo enviar el email.';
        this.snackBar.open(message, 'Cerrar', { duration: 4000 });
      },
    });
  }

  downloadPdf() {
    const current = this.invoice();
    if (!current) return;

    this.invoicesService.downloadPdf(current.id).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${current.invoice_number}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      },
      error: (err) => {
        const message = err?.error?.detail || 'No se pudo generar el PDF.';
        this.snackBar.open(message, 'Cerrar', { duration: 4000 });
      },
    });
  }
}
