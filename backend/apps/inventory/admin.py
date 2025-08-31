from django.contrib import admin

from .models import Category, Product

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active', 'created_at')
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass
