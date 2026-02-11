"""
Unit tests for custom permission classes
"""

from django.test import TestCase
from rest_framework.test import APIRequestFactory
from ..models import User
from ..permissions import (
    IsSuperAdmin,
    IsCountryAdminOrSuperAdmin,
    CanCreateUser,
    CanAlterUser,
)
from .test_utils import create_super_admin, create_country_admin, create_country_member


class IsSuperAdminTests(TestCase):
    """Test cases for IsSuperAdmin permission"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = IsSuperAdmin()
        self.super_admin = create_super_admin()
        self.country_admin = create_country_admin()
        self.member = create_country_member()

    def test_super_admin_has_permission(self):
        """Test Super Admin has permission"""
        request = self.factory.get("/api/test/")
        request.user = self.super_admin

        self.assertTrue(self.permission.has_permission(request, None))

    def test_country_admin_no_permission(self):
        """Test Country Admin does not have permission"""
        request = self.factory.get("/api/test/")
        request.user = self.country_admin

        self.assertFalse(self.permission.has_permission(request, None))

    def test_member_no_permission(self):
        """Test Country Member does not have permission"""
        request = self.factory.get("/api/test/")
        request.user = self.member

        self.assertFalse(self.permission.has_permission(request, None))


class IsCountryAdminOrSuperAdminTests(TestCase):
    """Test cases for IsCountryAdminOrSuperAdmin permission"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = IsCountryAdminOrSuperAdmin()
        self.super_admin = create_super_admin()
        self.country_admin = create_country_admin(country="USA")
        self.member = create_country_member(country="USA")
        self.other_country_user = create_country_member(
            email="other@test.com", country="Canada"
        )

    def test_super_admin_has_permission(self):
        """Test Super Admin has permission"""
        request = self.factory.get("/api/test/")
        request.user = self.super_admin

        self.assertTrue(self.permission.has_permission(request, None))

    def test_country_admin_has_permission(self):
        """Test Country Admin has permission"""
        request = self.factory.get("/api/test/")
        request.user = self.country_admin

        self.assertTrue(self.permission.has_permission(request, None))

    def test_member_no_permission(self):
        """Test Country Member does not have permission"""
        request = self.factory.get("/api/test/")
        request.user = self.member

        self.assertFalse(self.permission.has_permission(request, None))

    def test_super_admin_has_object_permission(self):
        """Test Super Admin has object-level permission for any object"""
        request = self.factory.get("/api/test/")
        request.user = self.super_admin

        # Super Admin can access objects from any country
        self.assertTrue(
            self.permission.has_object_permission(
                request, None, self.other_country_user
            )
        )

    def test_country_admin_has_object_permission_same_country(self):
        """Test Country Admin has object permission for same country"""
        request = self.factory.get("/api/test/")
        request.user = self.country_admin

        self.assertTrue(
            self.permission.has_object_permission(request, None, self.member)
        )

    def test_country_admin_no_object_permission_different_country(self):
        """Test Country Admin does not have object permission for different country"""
        request = self.factory.get("/api/test/")
        request.user = self.country_admin

        self.assertFalse(
            self.permission.has_object_permission(
                request, None, self.other_country_user
            )
        )


class CanCreateUserTests(TestCase):
    """Test cases for CanCreateUser permission"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = CanCreateUser()
        self.super_admin = create_super_admin()
        self.country_admin = create_country_admin(country="USA")
        self.member = create_country_member(country="USA")

    def test_member_cannot_create_users(self):
        """Test Country Member cannot create users"""
        request = self.factory.post("/api/users/", {"country": "USA"})
        request.user = self.member

        self.assertFalse(self.permission.has_permission(request, None))

    def test_unauthenticated_no_permission(self):
        """Test unauthenticated users cannot create users"""
        request = self.factory.post("/api/users/", {"country": "USA"})
        request.user = None

        self.assertFalse(self.permission.has_permission(request, None))


class CanAlterUserTests(TestCase):
    """Test cases for CanAlterUser permission"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = CanAlterUser()
        self.super_admin = create_super_admin()
        self.country_admin = create_country_admin(country="USA")
        self.member_usa = create_country_member(email="member1@test.com", country="USA")
        self.member_canada = create_country_member(
            email="member2@test.com", country="Canada"
        )

    def test_super_admin_can_alter_any_user(self):
        """Test Super Admin can alter users from any country"""
        request = self.factory.patch("/api/users/1/")
        request.user = self.super_admin

        self.assertTrue(
            self.permission.has_object_permission(request, None, self.member_canada)
        )
        self.assertTrue(
            self.permission.has_object_permission(request, None, self.member_usa)
        )

    def test_country_admin_can_alter_same_country(self):
        """Test Country Admin can alter users from same country"""
        request = self.factory.patch("/api/users/1/")
        request.user = self.country_admin

        self.assertTrue(
            self.permission.has_object_permission(request, None, self.member_usa)
        )

    def test_country_admin_cannot_alter_different_country(self):
        """Test Country Admin cannot alter users from different country"""
        request = self.factory.patch("/api/users/1/")
        request.user = self.country_admin

        self.assertFalse(
            self.permission.has_object_permission(request, None, self.member_canada)
        )
