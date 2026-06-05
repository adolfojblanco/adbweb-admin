import { Routes } from '@angular/router';
import { ClientsComponent } from './clients.component';
import { NewClientComponent } from './new-client/new-client.component';
import { ListClientsComponent } from './list-clients/list-clients.component';


export const clientsRoutes: Routes = [

{
  path: '',
  component: ClientsComponent,
  children: [
    {
      path: 'new',
      component: NewClientComponent
    },
    {
      path: 'lists',
      component: ListClientsComponent
    },
  ]
}

]

export default clientsRoutes
