import { Category } from './../../../models/category';
import { Component, computed, effect, inject, OnInit, signal } from '@angular/core';
import { CategoriesService } from '../../../services/categories.service';

@Component({
  selector: 'app-categories',
  imports: [],
  templateUrl: './categories.component.html',
  styles: ``
})
export class CategoriesComponent implements OnInit {
  private catService = inject(CategoriesService);
  public categories = signal<Category[]>([]);

  ngOnInit(): void {
    this.loadcategories();
  }

  loadcategories() {
    this.catService.loadCategories().subscribe(res => { this.categories.set(res) });
    console.log('Me ejecute');
  }

}
