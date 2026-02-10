from django.test import TestCase, override_settings
from django.urls import reverse
from django.core import mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from .models import User


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    SMS_PROVIDER='console',
)
class EmailAndSmsVerificationTests(TestCase):
    def test_signup_creates_inactive_user_and_sends_email(self):
        resp = self.client.post(reverse('signup'), {
            'username': 'alice',
            'email': 'alice@example.com',
            'phone': '09121234567',
            'role': 'student',
            'password1': 'StrongPass123!@#',
            'password2': 'StrongPass123!@#',
        })
        self.assertEqual(resp.status_code, 302)
        user = User.objects.get(username='alice')
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_email_verified)
        self.assertFalse(user.is_sms_verified)
        self.assertIsNotNone(user.sms_code)
        self.assertEqual(len(mail.outbox), 1)

    def test_verify_link_activates_user(self):
        user = User.objects.create_user(
            username='bob',
            email='bob@example.com',
            phone='09121234567',
            password='StrongPass123!@#',
            role='student',
            is_active=False,
            is_email_verified=False,
            is_sms_verified=False,
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        resp = self.client.get(reverse('verify_email', kwargs={'uidb64': uid, 'token': token}))
        self.assertEqual(resp.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_email_verified)
