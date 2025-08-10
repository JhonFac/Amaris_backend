import os
import sys


def main() -> int:
    # Configure Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'funds_management.settings')
    try:
        import django  # type: ignore
        django.setup()
    except Exception as exc:
        print(f"ERROR: could not initialize Django settings: {exc}")
        return 2

    from django.conf import settings  # noqa: E402
    from funds.notifications import NotificationService  # noqa: E402

    if len(sys.argv) < 2:
        print("Usage: python scripts/test_sms.py <to_phone> [message]")
        print("Example: python scripts/test_sms.py +573212777381 'Hola, prueba SMS' ")
        return 1

    to_phone = sys.argv[1]
    message = sys.argv[2] if len(sys.argv) >= 3 else 'Test SMS from Funds API'

    print("Twilio From:", getattr(settings, 'TWILIO_FROM_NUMBER', ''))
    print("Notifications enabled:", getattr(settings, 'NOTIFICATIONS_ENABLED', False))

    ok, info = NotificationService.send_sms(to_phone, message)
    print("Result:", ok)
    print("Info:", info)
    return 0 if ok else 3


if __name__ == '__main__':
    raise SystemExit(main())


