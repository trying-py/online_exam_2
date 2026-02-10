from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('instructor', 'Instructor'),
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student'
    )

    is_email_verified = models.BooleanField(default=False)

    phone = models.CharField(max_length=20, blank=True, null=True)
    is_sms_verified = models.BooleanField(default=False)
    sms_code = models.CharField(max_length=6, blank=True, null=True)
    sms_code_created_at = models.DateTimeField(blank=True, null=True)
