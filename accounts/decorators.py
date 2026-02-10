from __future__ import annotations

from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def email_verified_required(view_func):
    """Block access until the user verifies their email."""

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if request.user.is_authenticated and getattr(request.user, 'is_email_verified', False) is False:
            messages.warning(request, "لطفاً ابتدا ایمیل خود را تایید کنید.")
            return redirect('verify_sent')
        return view_func(request, *args, **kwargs)

    return _wrapped


def role_required(role: str):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if getattr(request.user, 'role', None) != role:
                messages.error(request, "شما اجازه دسترسی به این بخش را ندارید.")
                return redirect('exams:exam_list')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


instructor_required = role_required('instructor')
student_required = role_required('student')
