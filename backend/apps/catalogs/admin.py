from django.contrib import admin

from apps.catalogs.models import Product, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name", "slug")
    ordering = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display_links = ("sku", "name")
    list_display = ("sku", "name", "category", "sale_price", "cost_price", "is_active", "created_at")
    list_filter = ("is_active", "category")
    search_fields = ("sku", "name", "description")
    autocomplete_fields = ("category",)
    readonly_fields = ("sku", "created_at", "updated_at", "slug")
    ordering = ("-created_at",)
    list_editable = ('is_active',)
