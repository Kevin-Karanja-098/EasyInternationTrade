# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
import uuid


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, role, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not role:
            raise ValueError("Role is required")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            role=role,
            **extra_fields
        )

        # username auto-generated if missing
        if not user.username:
            user.username = uuid.uuid4().hex[:12]

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, role="importer", **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, role, **extra_fields)

    def create_superuser(self, email, password, role="admin", **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, password, role, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ("importer", "Importer"),
        ("supplier", "Supplier"),
        ("carrier", "Carrier"),
        ("warehouse", "Warehouse"),
        ("customs_agent", "Customs Agent"),
        ("admin", "Admin"),
    ]

    # MAIN FIX: Django requires a unique username for login
    username = models.CharField(max_length=150, unique=True, editable=False)

    # email is NOT unique (so same email can register multiple roles)
    email = models.EmailField("email address")

    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=50, blank=True)
    tax_id = models.CharField(max_length=128, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    verification_status = models.CharField(max_length=30, default="unverified")
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    # MAIN FIX: username is now the login field
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "role"]

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

        # MAIN FIX: same email can register multiple roles BUT only 1 per role
        constraints = [
            models.UniqueConstraint(
                fields=["email", "role"],
                name="unique_email_per_role"
            )
        ]

    def save(self, *args, **kwargs):
        # Assign username if not present
        if not self.username:
            self.username = uuid.uuid4().hex[:12]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} ({self.role})"
