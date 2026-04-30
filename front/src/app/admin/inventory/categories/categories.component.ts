import { Category } from './../../../models/category';
import { Component, inject, OnInit, signal } from '@angular/core';
import { CategoriesService } from '../../../services/categories.service';
import { MaterialModule } from '../../shared/material/material.module';
import { MatDialog } from '@angular/material/dialog';
import { DialogCategoriesComponent } from './dialog-categories/dialog-categories.component';


@Component({
  selector: 'app-categories',
  imports: [MaterialModule],
  templateUrl: './categories.component.html',
  styles: ``
})
export class CategoriesComponent implements OnInit {
  private dialog = inject(MatDialog);
  private catService = inject(CategoriesService);
  public categories = signal<Category[]>([]);
  public displayedColumns: string[] = ['name', 'active', 'actions'];

  public title = '';

  ngOnInit(): void {
    this.loadCategories();
  }

  loadCategories() {
    this.catService.loadCategories().subscribe(res => { this.categories.set(res) });
  }

  /** Add a new Category */
  newCategory() {
    const dialogRef = this.dialog.open(DialogCategoriesComponent, {
      width: '450px',
    });
    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.categories.update(prev => [...prev, result])
      }
    });
  }

  /** Edit a category */
  editCategory(category: Category) {
    const dialogRef = this.dialog.open(DialogCategoriesComponent, {
      width: '450px',
      data: category
    })
    dialogRef.afterClosed().subscribe(category => {
      if (category) {
        this.categories.update(categories => categories.map(c => c.id === category.id ? category : c))
      }
    })
  }


}
