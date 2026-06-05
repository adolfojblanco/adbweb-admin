import { Routes } from '@angular/router';
import { ClientsComponent } from './clients.component';
import { NewClientComponent } from './new-client/new-client.component';


export const clientsRoutes: Routes = [

{
  path: '',
  component: ClientsComponent,
  children: [
    {
      path: 'new',
      component: NewClientComponent
    }
  ]
}

]

export default clientsRoutes
