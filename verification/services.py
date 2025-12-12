from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings

def send_verification_email(user, token):
    verify_url = f"http://localhost:8000/verify-email/{token}/"

    subject = "Verify Your Email - EasyInternationalTrade"
    message = f"Click the link to verify your email: {verify_url}"
    
    # HTML version
    html_message = f"""
    <h2>Verify Your Email</h2>
    <p>Click the button below to verify your email:</p>
    <a href="{verify_url}"
       style="background:#00695c;color:white;padding:10px 20px;border-radius:5px;">
       Verify Email
    </a>
    <p>This link will expire in 24 hours.</p>
    """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
    )
