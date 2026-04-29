from django.contrib import admin

from apps.catalogs.models import Product, Category, Tax


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name", "slug")
    ordering = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display_links = ("sku", "name")
    list_display = ("sku", "name", "category", "sale_price", "cost_price", "active", "created_at")
    list_filter = ("active", "category", "tax")
    search_fields = ("sku", "name", "description")
    autocomplete_fields = ("category", "tax")
    readonly_fields = ("sku", "created_at", "updated_at", "slug")
    ordering = ("-created_at",)

    @admin.register(Tax)
    class TaxAdmin(admin.ModelAdmin):
        list_display = ("name", "percentage", "active")
        list_filter = ("active",)
        search_fields = ("name",)
