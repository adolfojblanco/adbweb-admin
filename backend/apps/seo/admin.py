from django.contrib import admin
from .models import SeoProject, SeoUrl, SeoAudit, SeoIssue, PageSpeedResult, AiSeoRecommendation,SeoOptimization


# Register your models here.

@admin.register(SeoProject)
class SeoProjectAdmin(admin.ModelAdmin):
    readonly_fields = ('created_by',)
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(SeoUrl)
class SeoUrlAdmin(admin.ModelAdmin):
    list_display = ("project", "label", "url", )


@admin.register(SeoAudit)
class SeoAuditAdmin(admin.ModelAdmin):
    list_display = (
        "seo_url",
        "status",
        "seo_score",
        "status_code",
        "created_at",
    )

    list_filter = (
        "status",
        "status_code",
        "has_sitemap",
        "has_robots_txt",
        "has_schema",
        "active",
    )

    search_fields = (
        "seo_url__url",
        "title",
        "meta_description",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "started_at",
        "completed_at",
    )

@admin.register(SeoIssue)
class SeoIssueAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "audit",
        "category",
        "severity",
        "is_fixed",
        "visible_to_client",
        "created_at",
    )

    list_filter = (
        "category",
        "severity",
        "is_fixed",
        "visible_to_client",
        "active",
    )

    search_fields = (
        "title",
        "description",
        "recommendation",
        "issue_type",
        "audit_seo_url_url",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

@admin.register(PageSpeedResult)
class PageSpeedResultAdmin(admin.ModelAdmin):
    list_display = (
        "audit",
        "mobile_score",
        "desktop_score",
        "lcp",
        "inp",
        "cls",
        "created_at",
    )

    list_filter = (
        "mobile_score",
        "desktop_score",
        "active",
    )

    search_fields = (
        "audit_seo_url_url",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "raw_data",
    )

@admin.register(AiSeoRecommendation)
class AiSeoRecommendationAdmin(admin.ModelAdmin):
    list_display = (
        "audit",
        "visible_to_client",
        "created_at",
    )

    list_filter = (
        "visible_to_client",
        "active",
    )

    search_fields = (
        "summary",
        "client_explanation",
        "admin_notes",
        "audit_seo_url_url",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

@admin.register(SeoOptimization)
class SeoOptimizationAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "project",
        "seo_url",
        "category",
        "status",
        "visible_to_client",
        "completed_at",
    )

    list_filter = (
        "category",
        "status",
        "visible_to_client",
        "active",
    )

    search_fields = (
        "title",
        "description",
        "before_value",
        "after_value",
        "project__domain",
        "seo_url__url",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )