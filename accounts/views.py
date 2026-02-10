from datetime import timedelta
import random

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone

from .forms import SignUpForm
from .models import User
from .sms import send_otp_sms


SMS_TTL_MINUTES = 10


def _generate_otp() -> str:
    return f"{random.randint(0, 999999):06d}"


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.is_email_verified = False
            user.is_sms_verified = False

            user.sms_code = _generate_otp()
            user.sms_code_created_at = timezone.now()
            user.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verify_link = f"{request.scheme}://{request.get_host()}/accounts/verify/{uid}/{token}/"

            subject = "فعال‌سازی حساب کاربری"
            message = render_to_string("accounts/verify_email.txt", {
                "user": user,
                "verify_link": verify_link,
            })

            if user.email:
                send_mail(subject, message, None, [
                          user.email], fail_silently=False)

            try:
                if user.phone:
                    send_otp_sms(user.phone, user.sms_code)
            except Exception as e:
                messages.warning(request, f"ارسال پیامک ناموفق بود: {e}")

            messages.success(
                request, "برای فعال‌سازی، لینک ایمیل یا کد پیامک را تایید کنید.")
            return redirect("verify_pending", uidb64=uid)
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})


def verify_pending_view(request, uidb64):
    return render(request, "accounts/verify_pending.html", {"uidb64": uidb64, "ttl": SMS_TTL_MINUTES})


def verify_sent_view(request):
    # Backward compatible
    return render(request, "accounts/verify_sent.html")


def verify_email_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_email_verified = True
        user.is_active = True
        user.save(update_fields=["is_active", "is_email_verified"])
        messages.success(
            request, "حساب شما با موفقیت با ایمیل فعال شد. حالا می‌توانید وارد شوید.")
        return render(request, "accounts/verify_success.html", {"user": user})

    return render(request, "accounts/verify_failed.html")


def verify_sms_view(request, uidb64):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if not user:
        messages.error(request, "کاربر یافت نشد.")
        return redirect("signup")

    if request.method == "POST":
        code = (request.POST.get("code") or "").strip()

        if not user.sms_code or not user.sms_code_created_at:
            messages.error(
                request, "کد پیامک برای این حساب موجود نیست. دوباره درخواست بده.")
            return redirect("verify_pending", uidb64=uidb64)

        if user.sms_code_created_at < timezone.now() - timedelta(minutes=SMS_TTL_MINUTES):
            messages.error(
                request, "کد منقضی شده است. لطفاً ارسال مجدد را بزن.")
            return redirect("verify_pending", uidb64=uidb64)

        if code == user.sms_code:
            user.is_sms_verified = True
            user.is_active = True
            user.sms_code = None
            user.save(update_fields=["is_active",
                      "is_sms_verified", "sms_code"])
            messages.success(
                request, "حساب شما با موفقیت با پیامک فعال شد. حالا می‌توانید وارد شوید.")
            return redirect("login")

        messages.error(request, "کد وارد شده اشتباه است.")
        return redirect("verify_sms", uidb64=uidb64)

    return render(request, "accounts/verify_sms.html", {"user": user, "uidb64": uidb64, "ttl": SMS_TTL_MINUTES})


def resend_sms_view(request, uidb64):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if not user:
        messages.error(request, "کاربر یافت نشد.")
        return redirect("signup")

    user.sms_code = _generate_otp()
    user.sms_code_created_at = timezone.now()
    user.save(update_fields=["sms_code", "sms_code_created_at"])

    try:
        if user.phone:
            send_otp_sms(user.phone, user.sms_code)
            messages.success(request, "کد جدید ارسال شد.")
        else:
            messages.error(request, "شماره موبایل برای این حساب ثبت نشده است.")
    except Exception as e:
        messages.error(request, f"ارسال پیامک ناموفق بود: {e}")

    return redirect("verify_pending", uidb64=uidb64)
