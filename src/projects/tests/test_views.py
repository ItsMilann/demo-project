"""
Integration tests for Project views and API endpoints
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.tests.test_utils import (
    create_super_admin,
    create_country_admin,
    create_country_member,
    get_authenticated_client,
)
from ..models import Project, AuditLog
from ..constants import ProjectStatus, AuditActionType


class ProjectViewSetListTests(APITestCase):
    """Test cases for listing projects"""

    def setUp(self):
        self.super_admin = create_super_admin()
        self.country_admin_usa = create_country_admin(
            email="admin_usa@test.com", country="USA"
        )
        self.member_usa = create_country_member(
            email="member_usa@test.com", country="USA"
        )
        self.member_canada = create_country_member(
            email="member_canada@test.com", country="Canada"
        )

        # Create projects in different countries
        self.project_usa = Project.objects.create(
            title="USA Project",
            description="Project in USA",
            status=ProjectStatus.ACTIVE,
            created_by=self.member_usa,
            country="USA",
        )
        self.project_canada = Project.objects.create(
            title="Canada Project",
            description="Project in Canada",
            status=ProjectStatus.DRAFT,
            created_by=self.member_canada,
            country="Canada",
        )

        print(f"DEBUG setUp: Count after creations: {Project.objects.all().count()}")
        for p in Project.objects.all():
            print(f"  Project: {p.title} ({p.country}) created by {p.created_by}")
        self.url = reverse("project-list")

    def test_super_admin_sees_all_projects(self):
        """Test Super Admin can see projects from all countries"""
        client = get_authenticated_client(self.super_admin)
        response = client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_country_admin_sees_only_their_country_projects(self):
        """Test Country Admin sees only projects from their country"""
        client = get_authenticated_client(self.country_admin_usa)
        response = client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "USA Project")

    def test_member_sees_only_their_country_projects(self):
        """Test Country Member sees only projects from their country"""
        client = get_authenticated_client(self.member_usa)
        response = client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["country"], "USA")

    def test_unauthenticated_cannot_list_projects(self):
        """Test unauthenticated request is denied"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_projects_by_status(self):
        """Test filtering projects by status"""
        client = get_authenticated_client(self.super_admin)
        response = client.get(self.url, {"status": ProjectStatus.ACTIVE})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["status"], ProjectStatus.ACTIVE)

    def test_filter_projects_by_country(self):
        """Test filtering projects by country"""
        client = get_authenticated_client(self.super_admin)
        response = client.get(self.url, {"country": "Canada"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["country"], "Canada")


class ProjectViewSetCreateTests(APITestCase):
    """Test cases for creating projects"""

    def setUp(self):
        self.user = create_country_member(country="USA")
        self.url = reverse("project-list")

    def test_create_project_requires_authentication(self):
        """Test creating project requires authentication"""
        data = {"title": "Test Project", "description": "Description"}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProjectViewSetUpdateTests(APITestCase):
    """Test cases for updating projects"""

    def setUp(self):
        self.super_admin = create_super_admin()
        self.member_usa = create_country_member(country="USA")
        self.member_canada = create_country_member(
            email="canada@test.com", country="Canada"
        )

        self.project_usa = Project.objects.create(
            title="USA Project",
            description="Description",
            created_by=self.member_usa,
            country="USA",
        )
        self.project_canada = Project.objects.create(
            title="Canada Project",
            description="Description",
            created_by=self.member_canada,
            country="Canada",
        )

    def test_update_project_success(self):
        """Test updating a project successfully"""
        client = get_authenticated_client(self.member_usa)
        url = reverse("project-detail", kwargs={"pk": self.project_usa.pk})
        data = {"title": "Updated Project", "status": ProjectStatus.ACTIVE}

        response = client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project_usa.refresh_from_db()
        self.assertEqual(self.project_usa.title, "Updated Project")
        self.assertEqual(self.project_usa.status, ProjectStatus.ACTIVE)

    def test_super_admin_can_update_any_project(self):
        """Test Super Admin can update projects from any country"""
        client = get_authenticated_client(self.super_admin)
        url = reverse("project-detail", kwargs={"pk": self.project_canada.pk})
        data = {"title": "Updated by Super Admin"}

        response = client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_member_cannot_update_different_country_project(self):
        """Test member cannot update projects from different country"""
        client = get_authenticated_client(self.member_usa)
        url = reverse("project-detail", kwargs={"pk": self.project_canada.pk})
        data = {"title": "Should fail"}

        response = client.patch(url, data, format="json")

        # Should not find the project (filtered by country)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ProjectViewSetDeleteTests(APITestCase):
    """Test cases for deleting projects"""

    def setUp(self):
        self.super_admin = create_super_admin()
        self.member_usa = create_country_member(country="USA")

        self.project = Project.objects.create(
            title="Test Project",
            description="Description",
            created_by=self.member_usa,
            country="USA",
        )

    def test_delete_project_success(self):
        """Test deleting a project successfully"""
        client = get_authenticated_client(self.member_usa)
        url = reverse("project-detail", kwargs={"pk": self.project.pk})

        response = client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())

    def test_super_admin_can_delete_any_project(self):
        """Test Super Admin can delete projects from any country"""
        client = get_authenticated_client(self.super_admin)
        url = reverse("project-detail", kwargs={"pk": self.project.pk})

        response = client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class AuditLogViewSetListTests(APITestCase):
    """Test cases for listing audit logs"""

    def setUp(self):
        self.super_admin = create_super_admin()
        self.member_usa = create_country_member(country="USA")
        self.member_canada = create_country_member(
            email="canada@test.com", country="Canada"
        )

        # Create projects
        self.project_usa = Project.objects.create(
            title="USA Project",
            description="Description",
            created_by=self.member_usa,
            country="USA",
        )
        self.project_canada = Project.objects.create(
            title="Canada Project",
            description="Description",
            created_by=self.member_canada,
            country="Canada",
        )

        # Create audit logs
        self.audit_usa = AuditLog.objects.create(
            user=self.member_usa,
            action_type=AuditActionType.CREATE,
            model_name="Project",
            object_id=self.project_usa.id,
        )
        self.audit_canada = AuditLog.objects.create(
            user=self.member_canada,
            action_type=AuditActionType.CREATE,
            model_name="Project",
            object_id=self.project_canada.id,
        )

        self.url = reverse("auditlog-list")

    def test_super_admin_sees_all_audit_logs(self):
        """Test Super Admin sees all audit logs"""
        client = get_authenticated_client(self.super_admin)
        response = client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should be 4 (2 from signal on project create + 2 manual)
        self.assertEqual(len(response.data["results"]), 4)

    def test_audit_logs_require_authentication(self):
        """Test audit logs require authentication"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
