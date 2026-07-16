from django.contrib import admin

from apps.catalogs.models import Product, Category, Tax, Service, ContractedService


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name", "slug")
    ordering = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display_links = ("sku", "name")
    list_display = ("sku", "name", "category", "sale_price", "cost_price", "is_active", "created_at")
    list_filter = ("is_active", "category", "tax")
    search_fields = ("sku", "name", "description")
    autocomplete_fields = ("category", "tax")
    readonly_fields = ("sku", "created_at", "updated_at", "slug")
    ordering = ("-created_at",)
    list_editable = ('is_active',)

@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ("name", "percentage", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_price', 'tax_percentage', 'is_active')
    list_editable = ('is_active',)

@admin.register(ContractedService)
class ContractedServiceAdmin(admin.ModelAdmin):
    list_display = ('customer', 'service', 'status', 'start_date', 'monthly_fee')
    list_filter = ('status', 'service')
    search_fields = ('customer__billing_name', 'service__name')

