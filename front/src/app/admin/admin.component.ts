import { Component } from '@angular/core';
import { RouterLink, RouterOutlet, RouterLinkActive } from '@angular/router';
import { NavBarComponent } from "./shared/nav-bar/nav-bar.component";



@Component({
  selector: 'app-admin',
  imports: [RouterOutlet, NavBarComponent],
  templateUrl: './admin.component.html',
  styles: ``
})
export class AdminComponent {

}
