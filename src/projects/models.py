from django.db import models
from django.conf import settings
from .constants import ProjectStatus as Status, AuditActionType as Action


class Project(models.Model):
    """
    Sample CRUD model for projects
    """

    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="projects",
    )
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "projects"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if "_current_user" in kwargs:
            self._current_user = kwargs.pop("_current_user")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class AuditLog(models.Model):
    """
    Audit log model to track all changes to models
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_logs",
    )
    action_type = models.CharField(max_length=10, choices=Action.choices)
    model_name = models.CharField(max_length=100)
    object_id = models.IntegerField()
    changes = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-timestamp"]

    def __str__(self):
        # fmt:off pylint:disable=line-too-long
        return f"{self.action_type} on {self.model_name}({self.object_id}) by {self.user} at {self.timestamp}"
