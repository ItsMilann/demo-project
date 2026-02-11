"""
Test utilities for creating test users and authentication
"""

from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import User


def create_super_admin(
    email="superadmin@test.com", password="Test@123", country="Global"
):
    """Create a super admin user for testing"""
    return User.objects.create_user(
        email=email,
        password=password,
        role=User.Role.SUPER_ADMIN,
        country=country,
    )


def create_country_admin(
    email="countryadmin@test.com", password="Test@123", country="USA"
):
    """Create a country admin user for testing"""
    return User.objects.create_user(
        email=email,
        password=password,
        role=User.Role.COUNTRY_ADMIN,
        country=country,
    )


def create_country_member(email="member@test.com", password="Test@123", country="USA"):
    """Create a country member user for testing"""
    return User.objects.create_user(
        email=email,
        password=password,
        role=User.Role.COUNTRY_MEMBER,
        country=country,
    )


def get_authenticated_client(user):
    """
    Create an authenticated API client with JWT token for the given user
    """
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


def get_tokens_for_user(user):
    """
    Generate JWT tokens for a user
    """
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
