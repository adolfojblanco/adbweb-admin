
import { Component, inject, OnInit, signal } from '@angular/core';
import { ProductsService } from '../../../services/products.service';
import { Product } from '../../../models/product';
import { MaterialModule } from '../../shared/material/material.module';
import { MatDialog } from '@angular/material/dialog';
import { DialogProductComponent } from './dialog-product/dialog-product.component';

@Component({
  selector: 'app-products',
  imports: [MaterialModule],
  templateUrl: './products.component.html',
  styles: ``
})
export class ProductsComponent implements OnInit {
  private productService = inject(ProductsService);
  private dialog = inject(MatDialog);
  public products = signal<Product[]>([]);
  public displayedColumns: string[] = ['sku', 'name', 'category', 'active', 'actions'];

  ngOnInit(): void {
    this.loadProducts();
  }

  loadProducts() {
    this.productService.loadProducts().subscribe(
      res => {
        this.products.set(res);
        console.log(res);
      }
    )
  }

  editProduct(product: Product): void {
    const dialogRef = this.dialog.open(DialogProductComponent, {
      width: '450px',
      data: product
    });
    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        //this.loadCategories();
      }
    });
  }

}
