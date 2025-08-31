from django.contrib import admin
from .models import Platform, ContentType

# Register your models here.
@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')

@admin.register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
