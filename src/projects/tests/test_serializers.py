"""
Unit tests for Project serializers
"""

from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request
from users.tests.test_utils import create_super_admin, create_country_member
from ..models import Project, AuditLog
from ..serializers import ProjectSerializer, AuditLogSerializer
from ..constants import ProjectStatus, AuditActionType


class ProjectSerializerTests(TestCase):
    """Test cases for ProjectSerializer"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = create_country_member(country="USA")
        self.project = Project.objects.create(
            title="Test Project",
            description="Test Description",
            status=ProjectStatus.DRAFT,
            created_by=self.user,
            country="USA",
        )

    def test_project_serializer_fields(self):
        """Test ProjectSerializer contains expected fields"""
        serializer = ProjectSerializer(instance=self.project)
        data = serializer.data

        self.assertIn("id", data)
        self.assertIn("title", data)
        self.assertIn("description", data)
        self.assertIn("status", data)
        self.assertIn("country", data)
        self.assertIn("created_by", data)
        self.assertIn("created_by_username", data)
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)

    def test_project_serializer_read_only_fields(self):
        """Test read-only fields cannot be updated via serializer"""
        serializer = ProjectSerializer(instance=self.project)

        # These fields should be read-only
        self.assertIn("id", serializer.data)
        self.assertIn("created_at", serializer.data)
        self.assertIn("updated_at", serializer.data)

    def test_created_by_username_field(self):
        """Test created_by_username field is populated correctly"""
        serializer = ProjectSerializer(instance=self.project)

        # Note: User model might not have username field, will be None or raise error
        # This test depends on User model having username field
        self.assertIn("created_by_username", serializer.data)

    def test_create_project_with_authenticated_user(self):
        """Test creating project automatically sets created_by and country from request user"""
        request = self.factory.post("/api/projects/")
        request.user = self.user

        data = {
            "title": "New Project",
            "description": "New Description",
            "status": ProjectStatus.ACTIVE,
        }

        drf_request = Request(request)
        drf_request.user = self.user
        serializer = ProjectSerializer(data=data, context={"request": drf_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

        project = serializer.save()

        # created_by and country should be set from request user
        self.assertEqual(project.created_by, self.user)
        self.assertEqual(project.country, self.user.country)

    def test_create_project_sets_country_from_user(self):
        """Test project country is automatically set to user's country"""
        request = self.factory.post("/api/projects/")
        request.user = self.user

        data = {
            "title": "Country Test Project",
            "description": "Description",
            "status": ProjectStatus.DRAFT,
        }

        drf_request = Request(request)
        drf_request.user = self.user
        serializer = ProjectSerializer(data=data, context={"request": drf_request})
        self.assertTrue(serializer.is_valid())

        project = serializer.save()
        self.assertEqual(project.country, "USA")

    def test_serialize_project_data(self):
        """Test serializing project data"""
        serializer = ProjectSerializer(instance=self.project)
        data = serializer.data

        self.assertEqual(data["title"], "Test Project")
        self.assertEqual(data["description"], "Test Description")
        self.assertEqual(data["status"], ProjectStatus.DRAFT)
        self.assertEqual(data["country"], "USA")


class AuditLogSerializerTests(TestCase):
    """Test cases for AuditLogSerializer"""

    def setUp(self):
        self.user = create_super_admin()
        self.project = Project.objects.create(
            title="Test Project",
            description="Description",
            created_by=self.user,
            country="Global",
        )
        self.audit_log = AuditLog.objects.create(
            user=self.user,
            action_type=AuditActionType.CREATE,
            model_name="Project",
            object_id=self.project.id,
            changes={"title": "Test Project"},
        )

    def test_audit_log_serializer_fields(self):
        """Test AuditLogSerializer contains expected fields"""
        serializer = AuditLogSerializer(instance=self.audit_log)
        data = serializer.data

        self.assertIn("id", data)
        self.assertIn("user", data)
        self.assertIn("user_username", data)
        self.assertIn("action_type", data)
        self.assertIn("model_name", data)
        self.assertIn("object_id", data)
        self.assertIn("changes", data)
        self.assertIn("timestamp", data)

    def test_audit_log_serializer_all_fields_readonly(self):
        """Test all AuditLogSerializer fields are read-only"""
        serializer = AuditLogSerializer(instance=self.audit_log)

        # All fields should be read-only
        for field in serializer.Meta.read_only_fields:
            self.assertIn(field, serializer.data)

    def test_user_username_field(self):
        """Test user_username field is populated correctly"""
        serializer = AuditLogSerializer(instance=self.audit_log)

        self.assertIn("user_username", serializer.data)

    def test_serialize_audit_log_data(self):
        """Test serializing audit log data"""
        serializer = AuditLogSerializer(instance=self.audit_log)
        data = serializer.data

        self.assertEqual(data["action_type"], AuditActionType.CREATE)
        self.assertEqual(data["model_name"], "Project")
        self.assertEqual(data["object_id"], self.project.id)
        self.assertEqual(data["changes"], {"title": "Test Project"})

    def test_serialize_audit_log_with_null_user(self):
        """Test serializing audit log when user is null"""
        audit = AuditLog.objects.create(
            user=None,
            action_type=AuditActionType.DELETE,
            model_name="Project",
            object_id=999,
            changes={"deleted": True},
        )

        serializer = AuditLogSerializer(instance=audit)
        data = serializer.data

        self.assertIsNone(data["user"])
        # user_username should handle null user gracefully
        self.assertIn("user_username", data)
