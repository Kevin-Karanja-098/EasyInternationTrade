# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
import uuid
from django.core.exceptions import ValidationError
from .utils import (
    id_front_upload_path, id_back_upload_path, dl_front_upload_path, dl_back_upload_path,
    business_license_upload_path, face_photo_upload_path
)


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

    REQUIRED_DOCUMENTS = {
    "importer": ["id_front", "id_back"],
    "supplier": ["business_license"],
    "carrier": ["id_front", "id_back"],
    "warehouse": ["business_license"],
    "customs_agent": ["id_front", "id_back", "business_license"],
}

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
    
    def check_verification_complete(self):
        required_docs = self.REQUIRED_DOCUMENTS.get(self.role, [])
        uploaded_docs = list(self.documents.values_list("doc_type", flat=True))

        for required in required_docs:
            if required not in uploaded_docs:
                return False

        return True

class Document(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)

    # NATIONAL ID
    id_front = models.FileField(upload_to=id_front_upload_path, blank=True, null=True)
    id_back = models.FileField(upload_to=id_back_upload_path, blank=True, null=True)
    dl_front = models.FileField(upload_to=dl_front_upload_path, blank=True, null=True)
    dl_back = models.FileField(upload_to=dl_back_upload_path, blank=True, null=True)
    business_license = models.FileField(upload_to=business_license_upload_path, blank=True, null=True)
    face_photo = models.FileField(upload_to=face_photo_upload_path, blank=True, null=True)

    is_verified = models.BooleanField(default=False)

    def clean(self):
        """
        Full validation logic using authenticated user's role:
        1. Importer MUST submit ONE of:
           - National ID (front + back)
           - OR Driver's License (front + back)
           - OR Business License
        2. Other roles MUST submit business license.
        3. No submitting only one side of ID or driver's license.
        """

        role = self.user.role  # <-- get role from the user

        # RULE 3: Prevent one-side-only uploads
        if (self.id_front and not self.id_back) or (self.id_back and not self.id_front):
            raise ValidationError("You must upload BOTH front and back of the National ID.")

        if (self.dl_front and not self.dl_back) or (self.dl_back and not self.dl_front):
            raise ValidationError("You must upload BOTH front and back of the Driver’s License.")

        # RULE 1: IMPORTER REQUIREMENTS
        if role == "importer":
            has_national_id = self.id_front and self.id_back
            has_driver_license = self.dl_front and self.dl_back
            has_business_license = self.business_license

            if not (has_national_id or has_driver_license or has_business_license):
                raise ValidationError(
                    "Importer must upload EITHER (ID front+back) OR (Driver License front+back) OR (Business License)."
                )

        # RULE 2: OTHER ROLES
        else:
            if not self.business_license:
                raise ValidationError("Business License is required for this role.")

        return super().clean()

    def __str__(self):
        return f"{self.user} - Documents"