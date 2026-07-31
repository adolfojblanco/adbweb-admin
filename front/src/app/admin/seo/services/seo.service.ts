import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';
import {
  Audit, AuditStatus, Issue, IssueCategory, IssueSeverity,
  Page, Paginated, Project,
} from '../interfaces/seo.interface';

@Injectable({ providedIn: 'root' })
export class SeoService {
  private readonly base = `${environment.apiUrl}/seo`;
  private http = inject(HttpClient);

  listProjects(search?: string): Observable<Project[]> {
    let params = new HttpParams();
    if (search) params = params.set('search', search);
    return this.http.get<Project[]>(`${this.base}/projects/`, { params });
  }

  createProject(payload: { name: string; domain: string }): Observable<Project> {
    return this.http.post<Project>(`${this.base}/projects/`, payload);
  }

  deleteProject(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/projects/${id}/`);
  }

  listAudits(filters: {
    page?: number;
    page_size?: number;
    project?: number;
    status?: AuditStatus;
    search?: string;
  } = {}): Observable<Paginated<Audit>> {
    const params = this.toParams(filters);
    return this.http.get<Paginated<Audit>>(`${this.base}/audits/`, { params });
  }

  getAudit(id: number): Observable<Audit> {
    return this.http.get<Audit>(`${this.base}/audits/${id}/`);
  }

  runAudit(id: number): Observable<{ detail: string }> {
    return this.http.post<{ detail: string }>(`${this.base}/audits/${id}/run/`, {});
  }

  createAudit(payload: { project: number; target_url: string; max_pages: number }): Observable<Audit> {
    return this.http.post<Audit>(`${this.base}/audits/`, payload);
  }

  deleteAudit(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/audits/${id}/`);
  }

  getPages(auditId: number, filters: {
    page?: number;
    status_code?: number;
    search?: string;
  } = {}): Observable<Paginated<Page>> {
    const params = this.toParams(filters);
    return this.http.get<Paginated<Page>>(`${this.base}/audits/${auditId}/pages/`, { params });
  }

  getIssues(auditId: number, filters: {
    page?: number;
    severity?: IssueSeverity;
    category?: IssueCategory;
  } = {}): Observable<Paginated<Issue>> {
    const params = this.toParams(filters);
    return this.http.get<Paginated<Issue>>(`${this.base}/audits/${auditId}/issues/`, { params });
  }

  private toParams(filters: Record<string, unknown>): HttpParams {
    let params = new HttpParams();
    Object.entries(filters).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') params = params.set(k, String(v));
    });
    return params;
  }
}
