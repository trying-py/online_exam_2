from django.conf import settings
from kavenegar import KavenegarAPI, APIException, HTTPException


def send_otp_sms(phone: str, code: str):
    if getattr(settings, "SMS_PROVIDER", "console") != "kavenegar":
        print(f"[SMS-CONSOLE] to={phone} code={code}")
        return None

    api_key = getattr(settings, "KAVENEGAR_API_KEY", "")
    sender = getattr(settings, "KAVENEGAR_SENDER", "")

    if not api_key:
        raise ValueError("KAVENEGAR_API_KEY is not set")
    if not sender:
        raise ValueError("KAVENEGAR_SENDER is not set")

    api = KavenegarAPI(api_key)
    params = {
        "sender": sender,
        "receptor": phone,
        "message": f"کد تایید شما: {code}",
    }

    try:
        return api.sms_send(params)
    except (APIException, HTTPException) as e:
        raise RuntimeError(f"Kavenegar SMS failed: {e}")
