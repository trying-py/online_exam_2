from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=True, help_text="مثال: 09121234567")
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css = 'form-control'
            if name == 'role':
                css = 'form-select'
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{existing} {css}".strip()

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if phone.startswith("+98"):
            phone = "0" + phone[3:]
        if not phone.startswith("09") or len(phone) != 11 or not phone.isdigit():
            raise forms.ValidationError(
                "شماره موبایل معتبر نیست. (مثال: 09121234567)")
        return phone

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "phone", "role")
