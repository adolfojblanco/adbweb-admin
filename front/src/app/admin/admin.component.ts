import { Component, signal } from '@angular/core';
import { RouterLink, RouterOutlet } from '@angular/router';
import { MaterialModule } from './shared/material/material.module';



@Component({
  selector: 'app-admin',
  imports: [RouterOutlet, MaterialModule, RouterLink],
  templateUrl: './admin.component.html',
  styles: ``
})
export class AdminComponent {

  appName = signal('ADB Web & Design');

    public sidebarItems = [
    { label: 'Inicio', icon: 'home', url: './' },
    { label: 'Categorias', icon: 'category', url: './inventory/categories' },
    { label: 'Productos', icon: 'inventory_2', url: './inventory/products' },
    { label: 'Facturas', icon: 'receipt', url: './invoice/new' },
    { label: 'Metodos de Pago', icon: 'credit_card_gear', url: './invoice/payment-methods'},
    { label: 'Proveedores', icon: 'source_environment', url: './invoice/suppliers' },
    { label: 'Usuarios', icon: 'groups', url: './users' },
  ];

}
