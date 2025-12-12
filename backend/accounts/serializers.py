# accounts/serializers.py
from rest_framework import serializers
from .models import User
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            "id",
            "id_front",
            "id_back",
            "dl_front",
            "dl_back",
            "business_license",
            "face_photo",
            "is_verified",
        ]
        read_only_fields = ["is_verified"]

    def create(self, validated_data):
        """
        Django model validation already enforces document rules.
        """
        document = Document(**validated_data)
        document.full_clean()  # triggers the validation logic in model.clean()
        document.save()
        return document
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "email", "password", "role", "first_name", "last_name", "company_name", "phone_number", "tax_id")
        read_only_fields = ("id",)

    def validate(self, data):
        # Enforce uniqueness of (email, role) at serializer level with friendlier error
        email = data.get("email")
        role = data.get("role")
        if User.objects.filter(email__iexact=email, role=role).exists():
            raise serializers.ValidationError({"detail": f"A user with email '{email}' already exists with role '{role}'."})
        return data

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "role", "first_name", "last_name", "company_name", "phone_number", "tax_id", "verified", "verification_status")
        read_only_fields = ("id", "verified", "verification_status")
