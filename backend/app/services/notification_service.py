import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import os
import json
from urllib import request as urlrequest
from urllib.error import URLError, HTTPError


class NotificationService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_pass = os.getenv("SMTP_PASS", "")
        self.default_from = os.getenv("SMTP_FROM", self.smtp_user)
        self.default_to = os.getenv("ALERT_EMAIL_TO", "")
        # Resend (preferred if available)
        self.resend_api_key = os.getenv("RESEND_API_KEY", "")
        self.resend_from = os.getenv("RESEND_FROM", "")
        self.last_error: str = ""

    def send_email(self, subject: str, body: str, to_emails: Optional[List[str]] = None, html_body: Optional[str] = None) -> bool:
        self.last_error = ""
        recipients = to_emails if to_emails else ([self.default_to] if self.default_to else [])
        # Normalize recipients (comma-separated supported)
        if len(recipients) == 1 and isinstance(recipients[0], str) and "," in recipients[0]:
            recipients = [e.strip() for e in recipients[0].split(',') if e.strip()]

        # Prefer Resend if configured
        if self.resend_api_key and self.resend_from and recipients:
            try:
                data = {
                    "from": self.resend_from,
                    "to": recipients,
                    "subject": subject,
                    "text": body,
                }
                if html_body:
                    data["html"] = html_body
                req = urlrequest.Request(
                    url="https://api.resend.com/emails",
                    data=json.dumps(data).encode("utf-8"),
                    headers={
                        "Authorization": f"Bearer {self.resend_api_key}",
                        "Content-Type": "application/json",
                    },
                    method="POST",
                )
                with urlrequest.urlopen(req, timeout=15) as resp:
                    return 200 <= resp.getcode() < 300
            except HTTPError as e:
                try:
                    body_text = e.read().decode("utf-8")
                except Exception:
                    body_text = ""
                self.last_error = f"HTTPError {e.code}: {body_text or str(e)}"
            except URLError as e:
                self.last_error = f"URLError: {getattr(e, 'reason', str(e))}"
            except Exception as e:
                self.last_error = str(e)
                # Fall back to SMTP if Resend fails
                pass

        # SMTP fallback
        if not recipients or not self.smtp_user or not self.smtp_pass:
            return False

        # SMTP: send multipart/alternative if HTML provided
        msg = MIMEMultipart("alternative") if html_body else MIMEMultipart()
        msg["From"] = self.default_from
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))
        if html_body:
            msg.attach(MIMEText(html_body, "html", "utf-8"))

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.sendmail(self.default_from, recipients, msg.as_string())
            return True
        except Exception as e:
            self.last_error = str(e)
            return False


