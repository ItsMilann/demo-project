from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "role", "country", "is_active", "date_joined")
    list_filter = ("role", "country", "is_active")
    search_fields = ("email", "country")
    ordering = ("-date_joined",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("username",)}),
        (
            "Permissions",
            {"fields": ("role", "country", "is_active", "is_staff", "is_superuser")},
        ),
        ("Important dates", {"fields": ("date_joined",)}),
    )

    readonly_fields = ("date_joined",)
