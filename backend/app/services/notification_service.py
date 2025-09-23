import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import os


class NotificationService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_pass = os.getenv("SMTP_PASS", "")
        self.default_from = os.getenv("SMTP_FROM", self.smtp_user)
        self.default_to = os.getenv("ALERT_EMAIL_TO", "")

    def send_email(self, subject: str, body: str, to_emails: Optional[List[str]] = None) -> bool:
        recipients = to_emails if to_emails else ([self.default_to] if self.default_to else [])
        if not recipients or not self.smtp_user or not self.smtp_pass:
            return False

        msg = MIMEMultipart()
        msg["From"] = self.default_from
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.sendmail(self.default_from, recipients, msg.as_string())
            return True
        except Exception:
            return False


