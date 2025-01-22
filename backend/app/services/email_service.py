from typing import List, Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from app.core.config import settings
import base64
from pathlib import Path

class EmailService:
    def __init__(self):
        self.client = SendGridAPIClient(settings.SMTP_PASSWORD)
        self.from_email = settings.EMAILS_FROM_EMAIL
        self.from_name = settings.EMAILS_FROM_NAME

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        attachments: Optional[List[tuple]] = None
    ) -> bool:
        """Send email using SendGrid"""
        message = Mail(
            from_email=(self.from_email, self.from_name),
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )

        if attachments:
            for attachment_path, filename in attachments:
                with open(attachment_path, 'rb') as f:
                    file_content = base64.b64encode(f.read()).decode()
                    attached_file = Attachment(
                        FileContent(file_content),
                        FileName(filename),
                        FileType('application/pdf'),
                        Disposition('attachment')
                    )
                    message.attachment = attached_file

        try:
            self.client.send(message)
            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False

    def send_welcome_email(self, to_email: str, username: str) -> bool:
        """Send welcome email after registration"""
        subject = "Welcome to PM Tool"
        content = f"""
        <h2>Welcome to PM Tool!</h2>
        <p>Dear {username},</p>
        <p>Thank you for registering with PM Tool. We're excited to help you manage your projects more efficiently.</p>
        <p>You can now:</p>
        <ul>
            <li>Create and manage projects</li>
            <li>Upload PDFs for automatic task extraction</li>
            <li>Sync your tasks with your calendar</li>
        </ul>
        <p>If you have any questions, please don't hesitate to contact us.</p>
        <p>Best regards,<br>PM Tool Team</p>
        """
        return self.send_email(to_email, subject, content)

    def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """Send password reset email"""
        reset_url = f"https://pm.bow-agentur.de/reset-password?token={reset_token}"
        subject = "Password Reset Request"
        content = f"""
        <h2>Password Reset Request</h2>
        <p>You have requested to reset your password. Click the link below to proceed:</p>
        <p><a href="{reset_url}">Reset Password</a></p>
        <p>If you didn't request this, please ignore this email.</p>
        <p>Best regards,<br>PM Tool Team</p>
        """
        return self.send_email(to_email, subject, content)

    def send_payment_confirmation(
        self,
        to_email: str,
        package_name: str,
        amount: float,
        invoice_path: str
    ) -> bool:
        """Send payment confirmation with invoice"""
        subject = f"Payment Confirmation - {package_name} Package"
        content = f"""
        <h2>Payment Confirmation</h2>
        <p>Thank you for your payment of €{amount:.2f} for the {package_name} package.</p>
        <p>Your subscription has been activated. You can find your invoice attached to this email.</p>
        <p>Best regards,<br>PM Tool Team</p>
        """
        attachments = [(invoice_path, "invoice.pdf")]
        return self.send_email(to_email, subject, content, attachments)

    def send_subscription_expiry_notice(self, to_email: str, days_left: int) -> bool:
        """Send subscription expiry notice"""
        subject = "Subscription Expiry Notice"
        content = f"""
        <h2>Subscription Expiry Notice</h2>
        <p>Your PM Tool subscription will expire in {days_left} days.</p>
        <p>To ensure uninterrupted service, please renew your subscription.</p>
        <p><a href="https://pm.bow-agentur.de/subscription">Renew Subscription</a></p>
        <p>Best regards,<br>PM Tool Team</p>
        """
        return self.send_email(to_email, subject, content)
