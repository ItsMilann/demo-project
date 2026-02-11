from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import Project, AuditLog
import json


# Store original state for comparison
_original_state = {}


@receiver(pre_save, sender=Project)
def store_original_state(sender, instance, **kwargs):
    """
    Store the original state of the project before update
    """
    if instance.pk:
        try:
            original = Project.objects.get(pk=instance.pk)
            _original_state[instance.pk] = {
                "title": original.title,
                "description": original.description,
                "status": original.status,
                "country": original.country,
            }
        except Project.DoesNotExist:
            pass


@receiver(post_save, sender=Project)
def log_project_create_update(sender, instance, created, **kwargs):
    """
    Log project creation and updates
    """
    user = getattr(instance, "_current_user", None)
    from .constants import AuditActionType as Action

    if created:
        AuditLog.objects.create(
            user=user or instance.created_by,
            action_type=Action.CREATE,
            model_name="Project",
            object_id=instance.pk,
            changes={
                "title": instance.title,
                "description": instance.description,
                "status": instance.status,
                "country": instance.country,
                "created_by": (
                    instance.created_by.username if instance.created_by else None
                ),
            },
        )
    else:
        changes = {}
        original = _original_state.get(instance.pk, {})

        for field in ["title", "description", "status", "country"]:
            old_value = original.get(field)
            new_value = getattr(instance, field)
            if old_value != new_value:
                changes[field] = {"old": old_value, "new": new_value}
        if changes:
            AuditLog.objects.create(
                user=user or instance.created_by,
                action_type=Action.UPDATE,
                model_name="Project",
                object_id=instance.pk,
                changes=changes,
            )
        if instance.pk in _original_state:  # cleanup
            del _original_state[instance.pk]


@receiver(post_delete, sender=Project)
def log_project_delete(sender, instance, **kwargs):
    """
    Log project deletion
    """
    user = getattr(instance, "_current_user", None)
    from .constants import AuditActionType as Action

    AuditLog.objects.create(
        user=user,
        action_type=Action.DELETE,
        model_name="Project",
        object_id=instance.pk,
        changes={
            "title": instance.title,
            "description": instance.description,
            "status": instance.status,
            "deleted": True,
        },
    )
