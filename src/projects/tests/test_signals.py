"""
Integration tests for audit logging signals
"""

from django.test import TestCase
from users.tests.test_utils import create_country_member
from ..models import Project, AuditLog
from ..constants import ProjectStatus, AuditActionType


class ProjectSignalsTests(TestCase):
    """Test cases for project audit logging signals"""

    def setUp(self):
        self.user = create_country_member(country="USA")

    def test_audit_log_created_on_project_create(self):
        """Test audit log is created when project is created"""
        project = Project.objects.create(
            title="New Project",
            description="Description",
            status=ProjectStatus.DRAFT,
            created_by=self.user,
            country="USA",
        )

        # Check audit log was created
        self.assertEqual(AuditLog.objects.count(), 1)

        audit = AuditLog.objects.first()
        self.assertEqual(audit.action_type, AuditActionType.CREATE)
        self.assertEqual(audit.model_name, "Project")
        self.assertEqual(audit.object_id, project.id)
        self.assertIn("title", audit.changes)
        self.assertEqual(audit.changes["title"], "New Project")

    def test_audit_log_created_on_project_update(self):
        """Test audit log is created when project is updated"""
        project = Project.objects.create(
            title="Original Title",
            description="Original Description",
            status=ProjectStatus.DRAFT,
            created_by=self.user,
            country="USA",
        )

        # Clear the create audit log
        AuditLog.objects.all().delete()

        # Update project
        project.title = "Updated Title"
        project.status = ProjectStatus.ACTIVE
        project._current_user = self.user
        project.save()

        # Check update audit log was created
        self.assertEqual(AuditLog.objects.count(), 1)

        audit = AuditLog.objects.first()
        self.assertEqual(audit.action_type, AuditActionType.UPDATE)
        self.assertEqual(audit.model_name, "Project")
        self.assertEqual(audit.object_id, project.id)

        # Check changes tracked
        self.assertIn("title", audit.changes)
        self.assertEqual(audit.changes["title"]["old"], "Original Title")
        self.assertEqual(audit.changes["title"]["new"], "Updated Title")

        self.assertIn("status", audit.changes)
        self.assertEqual(audit.changes["status"]["old"], ProjectStatus.DRAFT)
        self.assertEqual(audit.changes["status"]["new"], ProjectStatus.ACTIVE)

    def test_audit_log_only_tracks_changed_fields(self):
        """Test audit log only includes fields that actually changed"""
        project = Project.objects.create(
            title="Test Project",
            description="Description",
            status=ProjectStatus.DRAFT,
            created_by=self.user,
            country="USA",
        )

        AuditLog.objects.all().delete()

        # Update only title
        project.title = "New Title"
        project._current_user = self.user
        project.save()

        audit = AuditLog.objects.first()

        # Only title should be in changes
        self.assertIn("title", audit.changes)
        self.assertNotIn("description", audit.changes)  # Unchanged
        self.assertNotIn("country", audit.changes)  # Unchanged

    def test_audit_log_created_on_project_delete(self):
        """Test audit log is created when project is deleted"""
        project = Project.objects.create(
            title="Project to Delete",
            description="Will be deleted",
            status=ProjectStatus.ACTIVE,
            created_by=self.user,
            country="USA",
        )

        project_id = project.id
        project_title = project.title

        AuditLog.objects.all().delete()

        # Delete project
        project._current_user = self.user
        project.delete()

        # Check delete audit log was created
        self.assertEqual(AuditLog.objects.count(), 1)

        audit = AuditLog.objects.first()
        self.assertEqual(audit.action_type, AuditActionType.DELETE)
        self.assertEqual(audit.model_name, "Project")
        self.assertEqual(audit.object_id, project_id)
        self.assertIn("title", audit.changes)
        self.assertEqual(audit.changes["title"], project_title)
        self.assertTrue(audit.changes.get("deleted", False))

    def test_audit_log_captures_current_user_on_create(self):
        """Test audit log captures the current user on create"""
        project = Project.objects.create(
            title="Test Project",
            description="Description",
            created_by=self.user,
            country="USA",
        )
        project._current_user = self.user
        project.save()

        audit = AuditLog.objects.filter(action_type=AuditActionType.CREATE).first()

        # User should be captured (either from _current_user or created_by)
        self.assertIsNotNone(audit.user)

    def test_audit_log_captures_current_user_on_update(self):
        """Test audit log captures _current_user attribute on update"""
        project = Project.objects.create(
            title="Test Project",
            description="Description",
            created_by=self.user,
            country="USA",
        )

        AuditLog.objects.all().delete()

        # Update with _current_user set
        project.title = "Updated"
        project._current_user = self.user
        project.save()

        audit = AuditLog.objects.first()
        self.assertEqual(audit.user, self.user)

    def test_audit_log_no_update_log_if_no_changes(self):
        """Test no audit log created on update if nothing changed"""
        project = Project.objects.create(
            title="Test Project",
            description="Description",
            created_by=self.user,
            country="USA",
        )

        AuditLog.objects.all().delete()

        # Save without changes
        project._current_user = self.user
        project.save()

        # No update log should be created
        self.assertEqual(AuditLog.objects.count(), 0)

    def test_multiple_updates_create_multiple_audit_logs(self):
        """Test multiple updates create separate audit logs"""
        project = Project.objects.create(
            title="Test Project",
            description="Description",
            created_by=self.user,
            country="USA",
        )

        AuditLog.objects.all().delete()

        # First update
        project.title = "Update 1"
        project._current_user = self.user
        project.save()

        # Second update
        project.status = ProjectStatus.ACTIVE
        project._current_user = self.user
        project.save()

        # Should have 2 audit logs
        self.assertEqual(AuditLog.objects.count(), 2)

        audits = AuditLog.objects.order_by("-timestamp")
        self.assertEqual(audits[0].action_type, AuditActionType.UPDATE)
        self.assertEqual(audits[1].action_type, AuditActionType.UPDATE)
