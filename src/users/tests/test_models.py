"""
Unit tests for User model and UserManager
"""

from django.test import TestCase
from django.db import IntegrityError
from ..models import User


class UserManagerTests(TestCase):
    """Test cases for UserManager"""

    def test_create_user_success(self):
        """Test creating a user with valid data"""
        user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            role=User.Role.COUNTRY_MEMBER,
            country="USA",
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("testpass123"))
        self.assertEqual(user.role, User.Role.COUNTRY_MEMBER)
        self.assertEqual(user.country, "USA")

    def test_create_user_without_email(self):
        """Test creating a user without email raises error"""
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(
                email="",
                password="testpass123",
                role=User.Role.COUNTRY_MEMBER,
                country="USA",
            )
        self.assertIn("The Email must be set", str(context.exception))

    def test_create_user_email_normalized(self):
        """Test email is normalized for new users"""
        email = "test@EXAMPLE.COM"
        user = User.objects.create_user(
            email=email,
            password="testpass123",
            role=User.Role.COUNTRY_MEMBER,
            country="USA",
        )
        self.assertEqual(user.email, "test@example.com")

    def test_create_superuser(self):
        """Test creating a superuser with is_staff and is_superuser flags"""
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpass123",
            role=User.Role.SUPER_ADMIN,
            country="Global",
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_superuser_without_is_staff_flag(self):
        """Test creating superuser with is_staff=False raises error"""
        with self.assertRaises(ValueError) as context:
            User.objects.create_superuser(
                email="admin@example.com",
                password="adminpass123",
                is_staff=False,
                role=User.Role.SUPER_ADMIN,
                country="Global",
            )
        self.assertIn("Superuser must have is_staff=True", str(context.exception))


class UserModelTests(TestCase):
    """Test cases for User model"""

    def setUp(self):
        """Set up test users"""
        self.super_admin = User.objects.create_user(
            email="superadmin@test.com",
            password="Test@123",
            role=User.Role.SUPER_ADMIN,
            country="Global",
        )
        self.country_admin = User.objects.create_user(
            email="countryadmin@test.com",
            password="Test@123",
            role=User.Role.COUNTRY_ADMIN,
            country="USA",
        )
        self.country_member = User.objects.create_user(
            email="member@test.com",
            password="Test@123",
            role=User.Role.COUNTRY_MEMBER,
            country="USA",
        )

    def test_is_super_admin(self):
        """Test is_super_admin method"""
        self.assertTrue(self.super_admin.is_super_admin())
        self.assertFalse(self.country_admin.is_super_admin())
        self.assertFalse(self.country_member.is_super_admin())

    def test_is_country_admin(self):
        """Test is_country_admin method"""
        self.assertFalse(self.super_admin.is_country_admin())
        self.assertTrue(self.country_admin.is_country_admin())
        self.assertFalse(self.country_member.is_country_admin())

    def test_is_country_member(self):
        """Test is_country_member method"""
        self.assertFalse(self.super_admin.is_country_member())
        self.assertFalse(self.country_admin.is_country_member())
        self.assertTrue(self.country_member.is_country_member())

    def test_user_str_representation(self):
        """Test __str__ method returns email"""
        self.assertEqual(str(self.super_admin), "superadmin@test.com")
        self.assertEqual(str(self.country_admin), "countryadmin@test.com")

    def test_email_unique_constraint(self):
        """Test that duplicate emails raise IntegrityError"""
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email="superadmin@test.com",  # Duplicate email
                password="Test@123",
                role=User.Role.COUNTRY_MEMBER,
                country="Canada",
            )

    def test_username_field_is_email(self):
        """Test that USERNAME_FIELD is set to email"""
        self.assertEqual(User.USERNAME_FIELD, "email")

    def test_required_fields(self):
        """Test that REQUIRED_FIELDS includes role and country"""
        self.assertIn("role", User.REQUIRED_FIELDS)
        self.assertIn("country", User.REQUIRED_FIELDS)

    def test_role_choices(self):
        """Test that role choices are correctly defined"""
        self.assertEqual(User.Role.SUPER_ADMIN, "SUPER_ADMIN")
        self.assertEqual(User.Role.COUNTRY_ADMIN, "COUNTRY_ADMIN")
        self.assertEqual(User.Role.COUNTRY_MEMBER, "COUNTRY_MEMBER")

    def test_default_role(self):
        """Test default role is COUNTRY_MEMBER"""
        user = User(email="newuser@test.com", country="USA")
        self.assertEqual(user.role, User.Role.COUNTRY_MEMBER)
