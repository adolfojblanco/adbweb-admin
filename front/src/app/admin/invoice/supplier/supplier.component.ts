import { Component, effect, signal, viewChild } from '@angular/core';
import { MaterialModule } from '../../shared/material/material.module';
import { MatPaginator } from '@angular/material/paginator';
import { MatTableDataSource } from '@angular/material/table';
import { IsActivePipe } from '../../../pipes/is-active.pipe';

@Component({
  selector: 'app-supplier',
  imports: [MaterialModule, IsActivePipe],
  templateUrl: './supplier.component.html',
  styles: ``,
})
export class SupplierComponent {
// supplierService = inject(SupplierService);

  // 1. Definimos las columnas exactas de tu modelo Django + Acciones
  displayedColumns: string[] = ['name', 'phone', 'email', 'actions'];

  // 2. El Signal que recibe los datos crudos de tu base de datos
  suppliers = signal<any[]>([]);

  // 3. El DataSource especial para que Angular Material pueda paginar y filtrar
  dataSource = new MatTableDataSource<any>([]);

  // 4. Capturamos el Paginador del HTML
  paginator = viewChild(MatPaginator);

  constructor() {
    // 5. El Effect que mantiene sincronizada la tabla con el Signal
    effect(() => {
      this.dataSource.data = this.suppliers();

      const pag = this.paginator();
      if (pag) {
        this.dataSource.paginator = pag;
      }
    });
  }

  ngOnInit() {
    // Aquí llamarías a tu backend:
    // this.supplierService.getAll().subscribe(res => this.suppliers.set(res));

    // Datos de prueba para que veas la tabla funcionando inmediatamente
    this.suppliers.set([
      { id: 1, name: 'Valento Textil', phone: '600123456', email: 'contacto@valento.es' },
      { id: 2, name: 'Suministros XYZ', phone: '600987654', email: 'ventas@xyz.com' },
      { id: 3, name: 'Papelera Nacional', phone: '', email: '' } // Simula los blank=True
    ]);
  }

  newSupplier() {
    console.log('Abrir modal o ir a ruta de crear');
  }

  editSupplier(supplier: any) {
    console.log('Editar', supplier);
  }
}
