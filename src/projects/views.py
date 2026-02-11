from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Project, AuditLog
from .serializers import ProjectSerializer, AuditLogSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Project CRUD operations with role-based filtering
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["status", "country", "created_by"]

    def get_queryset(self):
        user = self.request.user
        print(
            f"DEBUG View: user={user}, authenticated={user.is_authenticated}, role={getattr(user, 'role', 'N/A')}, is_super={user.is_super_admin()}"
        )
        if not user or not user.is_authenticated:
            return Project.objects.none()
        if user.is_super_admin():
            return Project.objects.all()
        return Project.objects.filter(country=user.country)

    def perform_create(self, serializer):
        """
        Save the project with current user for audit logging
        """
        serializer.save(_current_user=self.request.user)

    def perform_update(self, serializer):
        """
        Update the project with current user for audit logging
        """
        serializer.save(_current_user=self.request.user)

    def perform_destroy(self, instance):
        """
        Delete the project with current user for audit logging
        """
        # Set current user for signal handler
        instance._current_user = self.request.user
        instance.delete()


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing audit logs (read-only)
    Filters logs based on user permissions
    """

    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["action_type", "model_name", "object_id"]

    def get_queryset(self):
        """
        Filter audit logs based on user role:
        - Super Admin: can see all audit logs
        - Country Admin/Member: can see logs for projects in their country
        """
        user = self.request.user
        if not user or not user.is_authenticated:
            return AuditLog.objects.none()

        if user.is_super_admin():
            return AuditLog.objects.all()

        # Get project IDs from user's country
        project_ids = Project.objects.filter(country=user.country).values_list(
            "id", flat=True
        )
        # Return audit logs for those projects
        return AuditLog.objects.filter(model_name="Project", object_id__in=project_ids)

    @action(detail=False, methods=["get"])
    def recent(self, request):
        """
        Get recent audit logs (last 20)
        """
        queryset = self.get_queryset()[:20]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
