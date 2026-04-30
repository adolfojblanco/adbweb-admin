import { Component, inject, OnInit, signal } from '@angular/core';
import { RouterLink, RouterLinkActive } from "@angular/router";
import { AuthService } from '../../../services/auth.service';
import { User } from '../../../models/user';

@Component({
  selector: 'app-nav-bar',
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './nav-bar.component.html',
  styles: ``
})
export class NavBarComponent implements OnInit {

  authService = inject(AuthService);
  authUser = signal<User | null>(null);






  ngOnInit(): void {
    this.getAuthUSer()
  }


  getAuthUSer() {
    this.authService.getAuthUser().subscribe((res) => {
      this.authUser.set(res);
    })
  }

}
