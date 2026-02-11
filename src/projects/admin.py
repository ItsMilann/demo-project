from django.contrib import admin
from .models import Project, AuditLog


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
        "country",
        "created_by",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "country", "created_at")
    search_fields = ("title", "description")
    readonly_fields = ("created_at", "updated_at")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("model_name", "object_id", "action_type", "user", "timestamp")
    list_filter = ("action_type", "model_name", "timestamp")
    search_fields = ("model_name", "object_id")
    readonly_fields = (
        "user",
        "action_type",
        "model_name",
        "object_id",
        "changes",
        "timestamp",
    )

    def has_add_permission(self, request):
        # Audit logs should only be created automatically
        return False

    def has_change_permission(self, request, obj=None):
        # Audit logs should not be editable
        return False
