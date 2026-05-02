from django.contrib import admin

from apps.company.models import Company


# Register your models here.

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email_company")
    search_fields = ("name", "phone", "email_company")
