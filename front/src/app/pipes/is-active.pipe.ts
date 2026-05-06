import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'isActive',
})
export class IsActivePipe implements PipeTransform {

  transform(value: unknown, ...args: unknown[]): unknown {
    return value ? 'fs-3 bi bi-power text-success' : 'fs-3 bi bi-power text-danger'
  }

}
