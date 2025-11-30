import { Category } from './../../../models/category';
import { Component, ElementRef, inject, OnInit, signal, ViewChild } from '@angular/core';
import { CategoriesService } from '../../../services/categories.service';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
// @ts-ignore
const $: any = window['$'];

@Component({
  selector: 'app-categories',
  imports: [ReactiveFormsModule],
  templateUrl: './categories.component.html',
  styles: ``
})
export class CategoriesComponent implements OnInit {
  @ViewChild('modal') modal?: ElementRef;
  private catService = inject(CategoriesService);
  private fb = inject(FormBuilder);
  public categories = signal<Category[]>([]);
  public title = '';

  ngOnInit(): void {
    this.loadcategories();
  }

  openModal(title: string) {
    this.title = title;
    $(this.modal?.nativeElement).modal('show');
  }

  public categoryForm: FormGroup = this.fb.group({
    name: ['dfghj', Validators.required],
    active: ['']
  })

  closeModal() {
    $(this.modal?.nativeElement).modal('hide');
  }

  loadcategories() {
    this.catService.loadCategories().subscribe(res => { this.categories.set(res) });
  }

  editCategory(category: Category) {
    this.openModal('Edición de categoria');
    console.log(category);
    this.categoryForm.reset(category)
  }

}
