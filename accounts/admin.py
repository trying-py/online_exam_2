from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'phone', 'role',
        'is_email_verified', 'is_sms_verified',
        'is_active', 'is_staff'
    )

    fieldsets = UserAdmin.fieldsets + (
        ('Role & Verification', {'fields': ('role', 'phone', 'is_email_verified', 'is_sms_verified')}),
    )
