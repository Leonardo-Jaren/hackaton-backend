from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    avatar_url = models.URLField(max_length=500, blank=True, null=True)


class OTPVerification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='otps')
    otp_code = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OTP for {self.user.username} - {self.otp_code}"

