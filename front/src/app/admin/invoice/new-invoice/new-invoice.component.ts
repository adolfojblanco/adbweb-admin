import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../../services/auth.service';
import { MaterialModule } from '../../shared/material/material.module';

@Component({
  selector: 'app-new-invoice',
  imports: [FormsModule, MaterialModule],
  templateUrl: './new-invoice.component.html',
  styles: ``,
})
export class NewInvoiceComponent {
  authService = inject(AuthService);
  customers = signal<any[]>([]);
  showDropdown = signal(false);
  searchInput = signal<string>('');

  onSearch(query: string) {
    console.log(query);
  }


  searchCustomer() {
    const search = this.searchInput().trim();
    this.authService.customerSearch(search).subscribe((res) => {
      this.customers.set(res);
      console.log(res);
      this.showDropdown.set(true);
    })
  }

}
