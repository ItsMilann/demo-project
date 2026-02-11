from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User

_R = User.Role


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model - read operations
    """

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "country",
            "is_active",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating users with validation
    """

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password_confirm",
            "role",
            "country",
        ]

    def __can_create_user_type(self, creator, role, country):
        if not creator or not creator.is_authenticated:
            return False
        if creator.is_super_admin():
            return True
        if creator.is_country_admin():
            return str(role) == str(_R.COUNTRY_MEMBER) and country == creator.country
        return False

    def validate(self, attrs, **kwargs):
        """
        Validate password confirmation and role-based constraints
        """
        if attrs.get("password") != attrs.get("password_confirm"):
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        # Check if the requesting user can create this role / country user
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user and not user.is_authenticated:
            _req = getattr(request, "_request", None)
            if _req:
                user = getattr(_req, "user", user)

        country = attrs.get("country")
        if not user or not user.is_authenticated:
            raise serializers.ValidationError(
                "User must be authenticated to create new users."
            )
        can_create = self.__can_create_user_type(user, attrs.get("role"), country)
        if not can_create:
            e = "You can only create users with roles and countries you have permission to manage."
            raise serializers.ValidationError({"role": e})
        return attrs

    def create(self, validated_data):
        """
        Create user with hashed password
        """
        validated_data.pop("password_confirm", None)
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating users
    """

    class Meta:
        model = User
        fields = ["email", "country", "is_active"]


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration (public endpoint)
    """

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password_confirm", "country"]

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password_confirm"):
            err = "Password fields didn't match."
            raise serializers.ValidationError({"password": err})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm", None)
        # new users registering through this endpoint are always country members
        validated_data["role"] = _R.COUNTRY_MEMBER
        user = User.objects.create_user(**validated_data)
        return user
