from rest_framework import serializers
from .models import Project, AuditLog


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for Project CRUD operations
    """

    created_by_username = serializers.CharField(
        source="created_by.username", read_only=True
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "status",
            "country",
            "created_by",
            "created_by_username",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "country", "created_at", "updated_at"]

    def create(self, validated_data, **kwargs):
        """
        Create project with the current user as creator and their country
        """
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user and not user.is_authenticated:
            # For tests where DRF Request wrapper might not have authenticated yet
            _req = getattr(request, "_request", None)
            if _req:
                user = getattr(_req, "user", user)

        if user and user.is_authenticated:
            validated_data.setdefault("created_by", user)
            validated_data.setdefault("country", getattr(user, "country", ""))

        return Project.objects.create(**validated_data)


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Serializer for viewing audit logs (read-only)
    """

    user_username = serializers.SerializerMethodField()

    def get_user_username(self, obj):
        return obj.user.username if obj.user else None

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "user",
            "user_username",
            "action_type",
            "model_name",
            "object_id",
            "changes",
            "timestamp",
        ]
        read_only_fields = fields
