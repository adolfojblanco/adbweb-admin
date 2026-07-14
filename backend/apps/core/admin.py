from django.contrib import admin

from apps.core.models import Company, Tax


# CoreApp models here.

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_by')
    search_fields = ('name',)


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')


