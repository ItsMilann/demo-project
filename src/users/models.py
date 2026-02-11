from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    """
    Custom manager for User model where email is the unique identifier
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.SUPER_ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model with role-based access control and country assignment.
    """

    class Role(models.TextChoices):
        SUPER_ADMIN = "SUPER_ADMIN", "Super Admin"
        COUNTRY_ADMIN = "COUNTRY_ADMIN", "Country Admin"
        COUNTRY_MEMBER = "COUNTRY_MEMBER", "Country Member"

    username = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.COUNTRY_MEMBER,
    )
    country = models.CharField(max_length=100)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["role", "country"]

    class Meta:
        db_table = "users"
        ordering = ["-id"]

    def __str__(self):
        return f"{self.email}"

    def is_super_admin(self):
        return self.is_authenticated and self.role == self.Role.SUPER_ADMIN

    def is_country_admin(self):
        return self.is_authenticated and self.role == self.Role.COUNTRY_ADMIN

    def is_country_member(self):
        return self.is_authenticated and self.role == self.Role.COUNTRY_MEMBER

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        return self.is_active and (self.is_superuser or self.is_staff)

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        return self.is_active and (self.is_superuser or self.is_staff)


class Profile:
    def __init__(self):
        raise NotImplementedError("Out of scope.")
