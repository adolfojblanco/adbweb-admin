import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { HotToastService } from '@ngxpert/hot-toast';
import { ClientsService } from '../../../services/clients.service';
import { Client, CustomerType } from '../../../models/client';
import { MaterialModule } from '../../shared/material/material.module';

@Component({
  selector: 'app-detail-client',
  imports: [MaterialModule, RouterLink],
  templateUrl: './detail-client.component.html',
  styles: ``,
})
export class DetailClientComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private clientsService = inject(ClientsService);
  private toast = inject(HotToastService);

  client = signal<Client | null>(null);

  customerTypeLabel = computed(() => {
    const type = this.client()?.customer_type;
    if (type === CustomerType.COMPANY) return 'Empresa';
    if (type === CustomerType.PERSON) return 'Autónomo / Particular';
    return '—';
  });

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (Number.isNaN(id)) {
      this.toast.error('ID de cliente inválido.');
      this.router.navigate(['/admin/clients/lists']);
      return;
    }

    this.clientsService.getById(id).subscribe({
      next: (client) => {
        this.client.set(client);
      },
      error: () => {
        this.toast.error('No se pudo cargar el cliente.');
        this.router.navigate(['/admin/clients/lists']);
      },
    });
  }
}
