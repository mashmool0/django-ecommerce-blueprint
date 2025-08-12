from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, OTPCode


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ("phone_number", "email", "is_staff",
                    "is_active", "date_joined")
    list_filter = ("is_staff", "is_active")
    readonly_fields = ("last_login", "date_joined")
    ordering = ("-date_joined",)
    search_fields = ("phone_number", "email")
    fieldsets = (
        (None, {"fields": ("phone_number", "email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active",
         "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone_number", "email", "password1", "password2", "is_staff", "is_active"),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "first_name_fa",
                    "last_name_fa", "city", "sms_opt_in")
    search_fields = ("user__phone_number", "first_name_fa",
                     "last_name_fa", "city")


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "purpose",
                    "expires_at", "consumed_at", "attempts")
    list_filter = ("purpose",)
    search_fields = ("phone_number",)
