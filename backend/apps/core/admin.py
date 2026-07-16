from django.contrib import admin

from apps.core.models import Company, Tax


# CoreApp models here.

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_by')
    search_fields = ('name',)


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_by', 'updated_by')
    readonly_fields = ('created_by', 'updated_by')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


