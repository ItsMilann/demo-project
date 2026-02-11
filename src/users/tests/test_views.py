"""
Integration tests for User views and API endpoints
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import User
from .test_utils import (
    create_super_admin,
    create_country_admin,
    create_country_member,
    get_authenticated_client,
)


class RegisterViewTests(APITestCase):
    """Test cases for public user registration endpoint"""

    def test_register_new_user_success(self):
        """Test successful user registration"""
        url = reverse("register")
        data = {
            "email": "newuser@test.com",
            "password": "Test@123456",
            "password_confirm": "Test@123456",
            "country": "USA",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

        user = User.objects.get(email="newuser@test.com")
        self.assertEqual(user.role, User.Role.COUNTRY_MEMBER)
        self.assertEqual(user.country, "USA")

    def test_register_password_mismatch(self):
        """Test registration fails with password mismatch"""
        url = reverse("register")
        data = {
            "email": "newuser@test.com",
            "password": "Test@123456",
            "password_confirm": "Different@123",
            "country": "USA",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def test_register_no_authentication_required(self):
        """Test registration works without authentication"""
        url = reverse("register")
        data = {
            "email": "public@test.com",
            "password": "Test@123456",
            "password_confirm": "Test@123456",
            "country": "Canada",
        }

        # No credentials set, should still work
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class UserViewSetListTests(APITestCase):
    """Test cases for listing users"""

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
        self.url = reverse("user-list")

    def test_super_admin_sees_all_users(self):
        """Test Super Admin can see all users"""
        client = get_authenticated_client(self.super_admin)
        response = client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 4)  # All 4 users

    def test_member_sees_only_themselves(self):
        """Test Country Member sees only their own profile"""
        client = get_authenticated_client(self.member_usa)
        response = client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["email"], "member_usa@test.com")

    def test_unauthenticated_cannot_list_users(self):
        """Test unauthenticated request is denied"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserViewSetCreateTests(APITestCase):
    """Test cases for creating users"""

    def setUp(self):
        self.super_admin = create_super_admin()
        self.country_admin = create_country_admin(country="USA")
        self.member = create_country_member(country="USA")
        self.url = reverse("user-list")

    def test_super_admin_can_create_user_any_country(self):
        """Test Super Admin can create users in any country"""
        client = get_authenticated_client(self.super_admin)
        data = {
            "email": "newuser@test.com",
            "password": "Test@123456",
            "password_confirm": "Test@123456",
            "role": User.Role.COUNTRY_ADMIN,
            "country": "Canada",
        }

        response = client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="newuser@test.com").exists())

    def test_country_admin_can_create_member_same_country(self):
        """Test Country Admin can create members in their country"""
        client = get_authenticated_client(self.country_admin)
        data = {
            "email": "newmember@test.com",
            "password": "Test@123456",
            "password_confirm": "Test@123456",
            "role": User.Role.COUNTRY_MEMBER,
            "country": "USA",
        }

        response = client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_country_admin_cannot_create_user_different_country(self):
        """Test Country Admin cannot create users in different country"""
        client = get_authenticated_client(self.country_admin)
        data = {
            "email": "newmember@test.com",
            "password": "Test@123456",
            "password_confirm": "Test@123456",
            "role": User.Role.COUNTRY_MEMBER,
            "country": "Canada",
        }

        response = client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_member_cannot_create_users(self):
        """Test Country Member cannot create users"""
        client = get_authenticated_client(self.member)
        data = {
            "email": "newmember@test.com",
            "password": "Test@123456",
            "password_confirm": "Test@123456",
            "role": User.Role.COUNTRY_MEMBER,
            "country": "USA",
        }

        response = client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserViewSetUpdateTests(APITestCase):
    """Test cases for updating users"""

    def setUp(self):
        self.super_admin = create_super_admin()
        self.country_admin_usa = create_country_admin(country="USA")
        self.member_usa = create_country_member(
            email="member_usa@test.com", country="USA"
        )
        self.member_canada = create_country_member(
            email="member_canada@test.com", country="Canada"
        )

    def test_super_admin_can_update_any_user(self):
        """Test Super Admin can update users from any country"""
        client = get_authenticated_client(self.super_admin)
        url = reverse("user-detail", kwargs={"pk": self.member_canada.pk})
        data = {"email": "updated@test.com"}

        response = client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.member_canada.refresh_from_db()
        self.assertEqual(self.member_canada.email, "updated@test.com")

    def test_country_admin_can_update_same_country_user(self):
        """Test Country Admin can update users from their country"""
        client = get_authenticated_client(self.country_admin_usa)
        url = reverse("user-detail", kwargs={"pk": self.member_usa.pk})
        data = {"country": "USA"}  # Same country

        response = client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_country_admin_cannot_update_different_country_user(self):
        """Test Country Admin cannot update users from different country"""
        client = get_authenticated_client(self.country_admin_usa)
        url = reverse("user-detail", kwargs={"pk": self.member_canada.pk})
        data = {"email": "updated@test.com"}

        response = client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserViewSetDeleteTests(APITestCase):
    """Test cases for deleting users"""

    def setUp(self):
        self.super_admin = create_super_admin()
        self.country_admin_usa = create_country_admin(country="USA")
        self.member_usa = create_country_member(
            email="member_usa@test.com", country="USA"
        )
        self.member_canada = create_country_member(
            email="member_canada@test.com", country="Canada"
        )

    def test_super_admin_can_delete_any_user(self):
        """Test Super Admin can delete users from any country"""
        client = get_authenticated_client(self.super_admin)
        url = reverse("user-detail", kwargs={"pk": self.member_canada.pk})

        response = client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=self.member_canada.pk).exists())

    def test_country_admin_can_delete_same_country_user(self):
        """Test Country Admin can delete users from their country"""
        client = get_authenticated_client(self.country_admin_usa)
        url = reverse("user-detail", kwargs={"pk": self.member_usa.pk})

        response = client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_country_admin_cannot_delete_different_country_user(self):
        """Test Country Admin cannot delete users from different country"""
        client = get_authenticated_client(self.country_admin_usa)
        url = reverse("user-detail", kwargs={"pk": self.member_canada.pk})

        response = client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserViewSetMeEndpointTests(APITestCase):
    """Test cases for /me endpoint"""

    def test_me_endpoint_returns_current_user(self):
        """Test /me endpoint returns authenticated user's profile"""
        user = create_country_member()
        client = get_authenticated_client(user)
        url = reverse("user-me")

        response = client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], user.email)
        self.assertEqual(response.data["country"], user.country)

    def test_me_endpoint_requires_authentication(self):
        """Test /me endpoint requires authentication"""
        url = reverse("user-me")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
