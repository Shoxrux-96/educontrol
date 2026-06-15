import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional

from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self._enabled = all([
            settings.smtp_host,
            settings.smtp_port,
            settings.smtp_from_email,
        ])

    def _get_connection(self):
        if not self._enabled:
            return None
        if settings.smtp_use_tls:
            server = smtplib.SMTP(str(settings.smtp_host), settings.smtp_port)
            server.starttls()
        else:
            server = smtplib.SMTP(str(settings.smtp_host), settings.smtp_port)
        if settings.smtp_user and settings.smtp_pass:
            server.login(settings.smtp_user, settings.smtp_pass)
        return server

    def send_email(
        self,
        to: List[str],
        subject: str,
        body: str,
        html: Optional[str] = None,
    ) -> bool:
        if not self._enabled:
            logger.warning(f"SMTP not configured, cannot send email: {subject}")
            return False

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.smtp_from_email
        msg["To"] = ", ".join(to)

        msg.attach(MIMEText(body, "plain"))
        if html:
            msg.attach(MIMEText(html, "html"))

        try:
            server = self._get_connection()
            server.sendmail(settings.smtp_from_email, to, msg.as_string())
            server.quit()
            logger.info(f"Email sent: {subject} -> {to}")
            return True
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return False

    def send_alert_notification(self, alert_info: dict):
        subject = f"[EDU Control] Alert: {alert_info.get('rule_name', 'Unknown')}"
        body = (
            f"Alert: {alert_info.get('rule_name')}\n"
            f"Metric: {alert_info.get('metric')}\n"
            f"Actual: {alert_info.get('actual_value')}\n"
            f"Threshold: {alert_info.get('threshold')}\n"
            f"Time: {alert_info.get('triggered_at')}\n"
        )
        html = None
        to = [settings.smtp_from_email]
        self.send_email(to, subject, body, html)


email_service = EmailService()
