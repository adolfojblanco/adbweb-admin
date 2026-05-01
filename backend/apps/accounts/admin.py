from django.contrib import admin

from apps.accounts.models import User, CustomerUser


# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email')

@admin.register(CustomerUser)
class CustomerUserAdmin(admin.ModelAdmin):
    list_display = ('billing_name', 'tax_id', 'customer_type', 'contact_email')
    list_filter = ('customer_type',)
    search_fields = ('billing_name', 'tax_id', 'contact_email')