import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../../environments/environment';
import { LighthouseResult, Paginated } from '../interfaces/seo.interface';

@Injectable({ providedIn: 'root' })
export class LighthouseService {
  private readonly base = `${environment.apiUrl}/seo/lighthouse`;
  private http = inject(HttpClient);

  list(filters: {
    page?: number;
    page_size?: number;
    page?: string;
    page__audit?: string;
  } = {}): Observable<Paginated<LighthouseResult>> {
    const params = this.toParams(filters);
    return this.http.get<Paginated<LighthouseResult>>(`${this.base}/`, { params });
  }

  listForAudit(auditId: string, pageSize = 50): Observable<Paginated<LighthouseResult>> {
    const params = new HttpParams()
      .set('page__audit', auditId)
      .set('page_size', String(pageSize))
      .set('ordering', '-run_at');
    return this.http.get<Paginated<LighthouseResult>>(`${this.base}/`, { params });
  }

  latestForPage(pageId: string): Observable<LighthouseResult[]> {
    const params = new HttpParams()
      .set('page', pageId)
      .set('page_size', '1')
      .set('ordering', '-run_at');
    return this.http.get<Paginated<LighthouseResult>>(`${this.base}/`, { params })
      .pipe();
  }

  runForPage(pageId: string): Observable<{ detail: string }> {
    return this.http.post<{ detail: string }>(`${this.base}/run/`, { page_id: pageId });
  }

  private toParams(filters: Record<string, unknown>): HttpParams {
    let params = new HttpParams();
    Object.entries(filters).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') {
        params = params.set(k, String(v));
      }
    });
    return params;
  }
}
