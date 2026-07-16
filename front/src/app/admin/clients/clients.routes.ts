import { Routes } from '@angular/router';
import { ClientsComponent } from './clients.component';
import { NewClientComponent } from './new-client/new-client.component';
import { ListClientsComponent } from './list-clients/list-clients.component';
import { EditClientComponent } from './edit-client/edit-client.component';
import { DetailClientComponent } from './detail-client/detail-client.component';


export const clientsRoutes: Routes = [

{
  path: '',
  component: ClientsComponent,
  children: [
    {
      path: '',
      pathMatch: 'full',
      redirectTo: 'lists'
    },
    {
      path: 'new',
      component: NewClientComponent
    },
    {
      path: 'lists',
      component: ListClientsComponent
    },
    {
      path: 'edit/:id',
      component: EditClientComponent
    },
    {
      path: 'detail/:id',
      component: DetailClientComponent
    },
  ]
}

]

export default clientsRoutes
