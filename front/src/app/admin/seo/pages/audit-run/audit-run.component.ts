import { Component, inject, OnInit, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { MaterialModule } from '../../shared/material/material.module';
import { HotToastService } from '@ngxpert/hot-toast';
import { SeoService } from '../../services/seo.service';
import { Project } from '../../interfaces/seo.interface';

@Component({
  selector: 'app-audit-run',
  imports: [MaterialModule, ReactiveFormsModule, RouterLink],
  templateUrl: './audit-run.component.html',
  styles: ``,
})
export class AuditRunComponent implements OnInit {
  private fb = inject(FormBuilder);
  private seo = inject(SeoService);
  private toast = inject(HotToastService);
  private router = inject(Router);

  projects = signal<Project[]>([]);
  saving = signal(false);

  form = this.fb.group({
    project: [null as number | null, [Validators.required]],
    target_url: ['', [Validators.required, Validators.pattern(/^https?:\/\//)]],
    max_pages: [50, [Validators.required, Validators.min(1), Validators.max(500)]],
  });

  ngOnInit(): void {
    this.seo.listProjects().subscribe({
      next: (projects) => this.projects.set(projects),
      error: () => this.toast.error('No se pudieron cargar los proyectos.'),
    });
  }

  createProjectPrompt() {
    const name = prompt('Nombre del proyecto:');
    if (!name) return;
    const domain = prompt('Dominio (ej: example.com):');
    if (!domain) return;
    this.seo.createProject({ name, domain }).subscribe({
      next: (project) => {
        this.projects.update((prev) => [project, ...prev]);
        this.form.patchValue({ project: project.id });
        this.toast.success('Proyecto creado.');
      },
      error: () => this.toast.error('No se pudo crear el proyecto.'),
    });
  }

  submit() {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.saving.set(true);
    const value = this.form.value;
    this.seo.createAudit({
      project: value.project!,
      target_url: value.target_url!,
      max_pages: value.max_pages!,
    }).subscribe({
      next: (audit) => {
        this.saving.set(false);
        this.toast.success('Auditoría encolada. Te llevamos al detalle.');
        this.router.navigate(['/admin/seo/audit-detail', audit.id]);
      },
      error: (err) => {
        this.saving.set(false);
        this.toast.error(err?.error?.detail || 'No se pudo lanzar la auditoría.');
      },
    });
  }
}
