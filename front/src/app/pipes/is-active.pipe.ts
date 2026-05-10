import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'isActive',
})
export class IsActivePipe implements PipeTransform {

  transform(value: unknown, ...args: unknown[]): unknown {
    return value ? 'text-success' : 'text-danger'
  }

}
