from django.shortcuts import render
from django.http import HttpResponse
from .models import EmailVerificationToken

def verify_email(request, token):
    try:
        token_obj = EmailVerificationToken.objects.get(token=token)
    except EmailVerificationToken.DoesNotExist:
        return HttpResponse("Invalid verification link", status=400)

    if token_obj.is_expired():
        return HttpResponse("Verification link expired", status=400)

    user = token_obj.user
    user.verified = True
    user.verification_status = "approved"
    user.save()

    token_obj.delete()  # remove token after success

    return HttpResponse("Email verified successfully. You can now log in.")
