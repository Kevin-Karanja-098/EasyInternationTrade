from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from verification.models import EmailVerificationToken
from verification.services import send_verification_email

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def send_verification_signal(sender, instance, created, **kwargs):
    if created:
        token = EmailVerificationToken.objects.create(user=instance)
        send_verification_email(instance, token.token)
