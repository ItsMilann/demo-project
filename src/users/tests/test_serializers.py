"""
Unit tests for User serializers
"""

from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request
from ..models import User
from ..serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    RegisterSerializer,
)
from .test_utils import create_super_admin, create_country_admin, create_country_member


class UserSerializerTests(TestCase):
    """Test cases for UserSerializer"""

    def setUp(self):
        self.user = create_country_member(email="member@test.com", country="USA")

    def test_user_serializer_fields(self):
        """Test UserSerializer contains expected fields"""
        serializer = UserSerializer(instance=self.user)
        data = serializer.data

        self.assertIn("id", data)
        self.assertIn("email", data)
        self.assertIn("role", data)
        self.assertIn("country", data)
        self.assertEqual(data["email"], "member@test.com")
        self.assertEqual(data["country"], "USA")

    def test_user_serializer_read_only_fields(self):
        """Test that id and date_joined are read-only"""
        serializer = UserSerializer(instance=self.user)
        # Read-only fields should be in data but not writable
        self.assertIn("id", serializer.data)


class UserCreateSerializerTests(TestCase):
    """Test cases for UserCreateSerializer"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.super_admin = create_super_admin()
        self.country_admin = create_country_admin(country="USA")

    def test_password_confirmation_validation(self):
        """Test password and password_confirm must match"""
        request = self.factory.post("/api/users/")
        request.user = self.super_admin

        data = {
            "email": "newuser@test.com",
            "password": "Test@123",
            "password_confirm": "DifferentPassword",
            "role": User.Role.COUNTRY_MEMBER,
            "country": "USA",
        }

        drf_request = Request(request)
        drf_request.user = request.user
        serializer = UserCreateSerializer(data=data, context={"request": drf_request})
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_super_admin_can_create_any_user(self):
        """Test Super Admin can create users with any role and country"""
        request = self.factory.post("/api/users/")
        request.user = self.super_admin

        data = {
            "email": "newadmin@test.com",
            "password": "Test@123",
            "password_confirm": "Test@123",
            "role": User.Role.COUNTRY_ADMIN,
            "country": "Canada",
        }

        drf_request = Request(request)
        drf_request.user = request.user
        serializer = UserCreateSerializer(data=data, context={"request": drf_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_country_admin_can_create_member_in_same_country(self):
        """Test Country Admin can create members in their country"""
        request = self.factory.post("/api/users/")
        request.user = self.country_admin

        data = {
            "email": "newmember@test.com",
            "password": "Test@123",
            "password_confirm": "Test@123",
            "role": User.Role.COUNTRY_MEMBER,
            "country": "USA",
        }

        drf_request = Request(request)
        drf_request.user = request.user
        serializer = UserCreateSerializer(data=data, context={"request": drf_request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_country_admin_cannot_create_user_in_different_country(self):
        """Test Country Admin cannot create users in different country"""
        request = self.factory.post("/api/users/")
        request.user = self.country_admin

        data = {
            "email": "newmember@test.com",
            "password": "Test@123",
            "password_confirm": "Test@123",
            "role": User.Role.COUNTRY_MEMBER,
            "country": "Canada",  # Different country
        }

        drf_request = Request(request)
        drf_request.user = request.user
        serializer = UserCreateSerializer(data=data, context={"request": drf_request})
        self.assertFalse(serializer.is_valid())
        self.assertIn("role", serializer.errors)

    def test_country_admin_cannot_create_admin(self):
        """Test Country Admin cannot create other admins"""
        request = self.factory.post("/api/users/")
        request.user = self.country_admin

        data = {
            "email": "newadmin@test.com",
            "password": "Test@123",
            "password_confirm": "Test@123",
            "role": User.Role.COUNTRY_ADMIN,
            "country": "USA",
        }

        drf_request = Request(request)
        drf_request.user = request.user
        serializer = UserCreateSerializer(data=data, context={"request": drf_request})
        self.assertFalse(serializer.is_valid())
        self.assertIn("role", serializer.errors)

    def test_create_user_hashes_password(self):
        """Test that created user has hashed password"""
        request = self.factory.post("/api/users/")
        request.user = self.super_admin

        data = {
            "email": "newuser@test.com",
            "password": "Test@123",
            "password_confirm": "Test@123",
            "role": User.Role.COUNTRY_MEMBER,
            "country": "USA",
        }

        drf_request = Request(request)
        drf_request.user = request.user
        serializer = UserCreateSerializer(data=data, context={"request": drf_request})
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        # Password should be hashed, not stored as plain text
        self.assertNotEqual(user.password, "Test@123")
        self.assertTrue(user.check_password("Test@123"))

    def test_password_confirm_not_saved(self):
        """Test password_confirm field is not saved to database"""
        request = self.factory.post("/api/users/")
        request.user = self.super_admin

        data = {
            "email": "newuser@test.com",
            "password": "Test@123",
            "password_confirm": "Test@123",
            "role": User.Role.COUNTRY_MEMBER,
            "country": "USA",
        }

        drf_request = Request(request)
        drf_request.user = request.user
        serializer = UserCreateSerializer(data=data, context={"request": drf_request})
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        # password_confirm should not be an attribute
        self.assertFalse(hasattr(user, "password_confirm"))


class UserUpdateSerializerTests(TestCase):
    """Test cases for UserUpdateSerializer"""

    def setUp(self):
        self.user = create_country_member()

    def test_update_allowed_fields(self):
        """Test updating allowed fields"""
        data = {"email": "updated@test.com", "country": "Canada", "is_active": False}

        serializer = UserUpdateSerializer(instance=self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        self.assertEqual(updated_user.email, "updated@test.com")
        self.assertEqual(updated_user.country, "Canada")
        self.assertFalse(updated_user.is_active)


class RegisterSerializerTests(TestCase):
    """Test cases for RegisterSerializer (public registration)"""

    def test_register_new_user(self):
        """Test registering a new user through public endpoint"""
        data = {
            "email": "public@test.com",
            "password": "Test@123",
            "password_confirm": "Test@123",
            "country": "USA",
        }

        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        self.assertEqual(user.email, "public@test.com")
        self.assertEqual(user.country, "USA")
        # Should automatically assign COUNTRY_MEMBER role
        self.assertEqual(user.role, User.Role.COUNTRY_MEMBER)

    def test_register_password_validation(self):
        """Test password validation on registration"""
        data = {
            "email": "public@test.com",
            "password": "123",  # Too short
            "password_confirm": "123",
            "country": "USA",
        }

        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_register_password_mismatch(self):
        """Test password confirmation mismatch"""
        data = {
            "email": "public@test.com",
            "password": "Test@123",
            "password_confirm": "Different@123",
            "country": "USA",
        }

        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_register_assigns_country_member_role(self):
        """Test that registered users always get COUNTRY_MEMBER role"""
        data = {
            "email": "public@test.com",
            "password": "Test@123",
            "password_confirm": "Test@123",
            "country": "Canada",
        }

        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        # Role should be forced to COUNTRY_MEMBER
        self.assertEqual(user.role, User.Role.COUNTRY_MEMBER)
