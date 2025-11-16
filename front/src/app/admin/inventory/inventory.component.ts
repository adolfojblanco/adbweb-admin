import { Component, inject, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CategoriesService } from '../../services/categories.service';


@Component({
  selector: 'app-inventory',
  imports: [RouterOutlet],
  templateUrl: './inventory.component.html',
  styles: ``
})


export class InventoryComponent implements OnInit {


  private categoryServices = inject(CategoriesService);


  ngOnInit(): void {

  }




}
