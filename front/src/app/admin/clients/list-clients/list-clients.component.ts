import { Component, inject, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ClientsService } from '../../../services/clients.service';
import { Client } from '../../../models/client';
import { MaterialModule } from '../../shared/material/material.module';
import { HotToastService } from '@ngxpert/hot-toast';

@Component({
  selector: 'app-list-clients',
  imports: [MaterialModule, RouterLink],
  templateUrl: './list-clients.component.html',
  styles: ``,
})
export class ListClientsComponent implements OnInit {
  private clientsService = inject(ClientsService);
  private toast = inject(HotToastService);

  clients = signal<Client[]>([]);
  displayedColumns: string[] = ['id', 'billing_name', 'tax_id', 'contact_email', 'phone', 'user', 'actions'];

  ngOnInit(): void {
    this.loadClients();
  }

  loadClients() {
    this.clientsService.loadCustomers().subscribe((res) => {
      this.clients.set(res);
    });
  }

  deleteClient(client: Client) {
    const confirmed = window.confirm(`¿Eliminar el cliente "${client.billing_name}"? Esta acción no se puede deshacer.`);
    if (!confirmed || !client.id) return;

    this.clientsService.deleteCustomer(client.id).subscribe({
      next: () => {
        this.clients.update((list) => list.filter((c) => c.id !== client.id));
        this.toast.success('Cliente eliminado correctamente');
      },
      error: (err) => {
        const message = err?.error?.detail || 'No se pudo eliminar el cliente.';
        this.toast.error(message);
      },
    });
  }
}
