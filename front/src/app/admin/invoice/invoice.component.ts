import { Component, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-invoice',
  imports: [RouterOutlet],
  templateUrl: './invoice.component.html',
  styles: ``,
})
export class InvoiceComponent implements OnInit {

  ngOnInit(): void {
  }

}
