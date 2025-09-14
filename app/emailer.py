from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from .config import settings

def send_email(to_email: str, subject: str, html: str):
    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
    message = Mail(
        from_email=settings.FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html,
    )
    sg.send(message)
