from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError
from .models import Document
from .serializers import DocumentSerializer


class DocumentUploadView(generics.CreateAPIView):
    serializer_class = DocumentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        try:
            serializer.save(
                user=self.request.user,
                role=self.request.user.role
            )
        except ValidationError as e:
            # Convert Django ValidationError to DRF ValidationError
            raise DRFValidationError(e.message_dict)


class DocumentListView(generics.ListAPIView):
    serializer_class = DocumentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)
