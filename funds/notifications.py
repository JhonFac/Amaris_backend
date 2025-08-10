import logging
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import Tuple
from twilio.rest import Client
from django.conf import settings

try:
    from twilio.rest import Client as TwilioClient
except Exception:  # pragma: no cover
    TwilioClient = None

from .models import Client as ClientModel

logger = logging.getLogger(__name__)


class NotificationService:
    @staticmethod
    def send_email(to_email: str, subject: str, body: str) -> Tuple[bool, str]:
        if not settings.NOTIFICATIONS_ENABLED:
            return False, 'Notifications disabled'

        if not to_email:
            return False, 'Missing recipient email'

        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            return False, 'Email settings are not configured'

        try:
            msg = MIMEText(body, 'plain', 'utf-8')
            sender_email = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER
            msg['Subject'] = subject
            msg['From'] = formataddr(('Funds App', sender_email))
            msg['To'] = to_email

            with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                server.ehlo()
                if getattr(settings, 'EMAIL_USE_TLS', True):
                    server.starttls()
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                server.sendmail(sender_email, [to_email], msg.as_string())
            return True, 'Email sent'
        except Exception as exc:  # pragma: no cover
            logger.exception('Error sending email: %s', exc)
            return False, str(exc)

    @staticmethod
    def send_sms(to_phone: str, body: str) -> Tuple[bool, str]:
        if not settings.NOTIFICATIONS_ENABLED:
            return False, 'Notifications disabled'

        if not to_phone:
            return False, 'Missing recipient phone'

        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN or not settings.TWILIO_FROM_NUMBER:
            return False, 'Twilio settings are not configured'

        if TwilioClient is None:
            return False, 'Twilio client not available'

        try:
            # client = TwilioClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            # message = client.messages.create(
            #     body=body,
            #     from_=settings.TWILIO_FROM_NUMBER,
            #     to=to_phone,
            # )

            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message = client.messages.create(
              from_=settings.TWILIO_FROM_NUMBER,
              body=body,
              to=to_phone
            )
            return True, message.sid
        except Exception as exc:  # pragma: no cover
            logger.exception('Error sending SMS: %s', exc)
            return False, str(exc)

    @staticmethod
    def notify_client(client_id: str, subject: str, message: str) -> None:
        try:
            client = ClientModel.get_by_id(client_id)
            if not client:
                logger.warning('Client %s not found to notify', client_id)
                return

            print(client)
            print(client.email)
            print(client.phone)
            print(message)
            print(subject)

            if getattr(client, 'email', None):
                status, info = NotificationService.send_email(client.email, subject, message)
                print(status, info)
            if getattr(client, 'phone', None):
                status, info = NotificationService.send_sms(client.phone, message)
                print(status, info)
        except Exception as exc:  # pragma: no cover
            logger.exception('Error in notify_client: %s', exc)


