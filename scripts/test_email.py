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
        print("Usage: python scripts/test_email.py <to_email> [subject] [message]")
        print("Example: python scripts/test_email.py jhonfredyaya04@gmail.com 'Hola' 'Prueba correo' ")
        return 1

    to_email = sys.argv[1]
    subject = sys.argv[2] if len(sys.argv) >= 3 else 'Test Email from Funds API'
    message = sys.argv[3] if len(sys.argv) >= 4 else 'Esto es una prueba de correo.'

    print("From email:", getattr(settings, 'DEFAULT_FROM_EMAIL', ''))
    print("SMTP host:", getattr(settings, 'EMAIL_HOST', ''), getattr(settings, 'EMAIL_PORT', ''))
    print("Notifications enabled:", getattr(settings, 'NOTIFICATIONS_ENABLED', False))

    ok, info = NotificationService.send_email(to_email, subject, message)
    print("Result:", ok)
    print("Info:", info)
    return 0 if ok else 3


if __name__ == '__main__':
    raise SystemExit(main())


