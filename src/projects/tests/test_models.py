"""
Unit tests for Project and AuditLog models
"""

from django.test import TestCase
from users.tests.test_utils import create_super_admin, create_country_member
from ..models import Project, AuditLog
from ..constants import ProjectStatus, AuditActionType


class ProjectModelTests(TestCase):
    """Test cases for Project model"""

    def setUp(self):
        self.user = create_country_member(country="USA")

    def test_create_project(self):
        """Test creating a project with all fields"""
        project = Project.objects.create(
            title="Test Project",
            description="This is a test project",
            status=ProjectStatus.DRAFT,
            created_by=self.user,
            country="USA",
        )

        self.assertEqual(project.title, "Test Project")
        self.assertEqual(project.description, "This is a test project")
        self.assertEqual(project.status, ProjectStatus.DRAFT)
        self.assertEqual(project.created_by, self.user)
        self.assertEqual(project.country, "USA")

    def test_project_str_representation(self):
        """Test __str__ method returns title and status"""
        project = Project.objects.create(
            title="My Project",
            description="Description",
            status=ProjectStatus.ACTIVE,
            created_by=self.user,
            country="USA",
        )

        expected = f"My Project (Active)"
        self.assertEqual(str(project), expected)

    def test_project_default_status(self):
        """Test default status is DRAFT"""
        project = Project(
            title="Test Project",
            description="Description",
            created_by=self.user,
            country="USA",
        )

        self.assertEqual(project.status, ProjectStatus.DRAFT)

    def test_project_status_choices(self):
        """Test all project status choices"""
        self.assertEqual(ProjectStatus.DRAFT, "draft")
        self.assertEqual(ProjectStatus.ACTIVE, "active")
        self.assertEqual(ProjectStatus.COMPLETED, "completed")
        self.assertEqual(ProjectStatus.ARCHIVED, "archived")

    def test_project_created_at_auto_set(self):
        """Test created_at is automatically set"""
        project = Project.objects.create(
            title="Test Project",
            description="Description",
            created_by=self.user,
            country="USA",
        )

        self.assertIsNotNone(project.created_at)

    def test_project_updated_at_auto_updates(self):
        """Test updated_at is automatically updated"""
        project = Project.objects.create(
            title="Test Project",
            description="Description",
            created_by=self.user,
            country="USA",
        )

        original_updated_at = project.updated_at

        project.title = "Updated Title"
        project.save()
        project.refresh_from_db()

        self.assertGreater(project.updated_at, original_updated_at)

    def test_project_created_by_can_be_null(self):
        """Test created_by can be null (on delete SET_NULL)"""
        project = Project.objects.create(
            title="Test Project",
            description="Description",
            created_by=self.user,
            country="USA",
        )

        user_id = self.user.id
        self.user.delete()

        project.refresh_from_db()
        self.assertIsNone(project.created_by)


class AuditLogModelTests(TestCase):
    """Test cases for AuditLog model"""

    def setUp(self):
        self.user = create_super_admin()
        self.project = Project.objects.create(
            title="Test Project",
            description="Description",
            created_by=self.user,
            country="Global",
        )

    def test_create_audit_log(self):
        """Test creating an audit log"""
        audit = AuditLog.objects.create(
            user=self.user,
            action_type=AuditActionType.CREATE,
            model_name="Project",
            object_id=self.project.id,
            changes={"title": "Test Project"},
        )

        self.assertEqual(audit.user, self.user)
        self.assertEqual(audit.action_type, AuditActionType.CREATE)
        self.assertEqual(audit.model_name, "Project")
        self.assertEqual(audit.object_id, self.project.id)
        self.assertEqual(audit.changes, {"title": "Test Project"})

    def test_audit_log_str_representation(self):
        """Test __str__ method"""
        audit = AuditLog.objects.create(
            user=self.user,
            action_type=AuditActionType.UPDATE,
            model_name="Project",
            object_id=self.project.id,
            changes={},
        )

        str_repr = str(audit)
        self.assertIn("update", str_repr.lower())
        self.assertIn("Project", str_repr)
        self.assertIn(str(self.project.id), str_repr)

    def test_audit_log_action_type_choices(self):
        """Test all audit action type choices"""
        self.assertEqual(AuditActionType.CREATE, "create")
        self.assertEqual(AuditActionType.UPDATE, "update")
        self.assertEqual(AuditActionType.DELETE, "delete")

    def test_audit_log_default_changes(self):
        """Test changes field has default empty dict"""
        audit = AuditLog(
            user=self.user,
            action_type=AuditActionType.CREATE,
            model_name="Project",
            object_id=self.project.id,
        )

        self.assertEqual(audit.changes, {})

    def test_audit_log_timestamp_auto_set(self):
        """Test timestamp is automatically set"""
        audit = AuditLog.objects.create(
            user=self.user,
            action_type=AuditActionType.CREATE,
            model_name="Project",
            object_id=self.project.id,
        )

        self.assertIsNotNone(audit.timestamp)

    def test_audit_log_user_can_be_null(self):
        """Test user can be null (on delete SET_NULL)"""
        audit = AuditLog.objects.create(
            user=self.user,
            action_type=AuditActionType.DELETE,
            model_name="Project",
            object_id=self.project.id,
        )

        self.user.delete()
        audit.refresh_from_db()

        self.assertIsNone(audit.user)

    def test_audit_log_ordering(self):
        """Test audit logs are ordered by timestamp descending"""
        audit1 = AuditLog.objects.create(
            user=self.user,
            action_type=AuditActionType.CREATE,
            model_name="Project",
            object_id=1,
        )

        audit2 = AuditLog.objects.create(
            user=self.user,
            action_type=AuditActionType.UPDATE,
            model_name="Project",
            object_id=1,
        )

        logs = list(AuditLog.objects.all())
        self.assertEqual(logs[0], audit2)  # Most recent first
        self.assertEqual(logs[1], audit1)
