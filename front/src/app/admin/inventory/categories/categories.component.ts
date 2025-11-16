import { Category } from './../../../models/category';
import { Component, inject, signal } from '@angular/core';
import { CategoriesService } from '../../../services/categories.service';

@Component({
  selector: 'app-categories',
  imports: [],
  templateUrl: './categories.component.html',
  styles: ``
})
export class CategoriesComponent {

  private catService = inject(CategoriesService);
  public categories = signal<Category[]>([])

}
