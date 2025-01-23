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
        subject = "Willkommen bei PM Tool"
        content = f"""
        <h2>Willkommen bei PM Tool!</h2>
        <p>Sehr geehrte(r) {username},</p>
        <p>vielen Dank für Ihre Registrierung bei PM Tool. Wir freuen uns, Sie bei der effizienten Verwaltung Ihrer Projekte unterstützen zu dürfen.</p>
        <p>Sie können jetzt:</p>
        <ul>
            <li>Projekte erstellen und verwalten</li>
            <li>PDFs für die automatische Aufgabenextraktion hochladen</li>
            <li>Ihre Aufgaben mit Ihrem Kalender synchronisieren</li>
        </ul>
        <p>Bei Fragen stehen wir Ihnen gerne zur Verfügung.</p>
        <p>Mit freundlichen Grüßen<br>Ihr PM Tool Team</p>
        """
        try:
            return self.send_email(to_email, subject, content)
        except Exception as e:
            print(f"Failed to send welcome email to {to_email}: {str(e)}")
            return False

    def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """Send password reset email"""
        reset_url = f"https://pm.bow-agentur.de/reset-password?token={reset_token}"
        subject = "PM Tool Passwort zurücksetzen"
        content = f"""
        <h2>Passwort zurücksetzen</h2>
        <p>Sie haben eine Anfrage zum Zurücksetzen Ihres Passworts gestellt. Klicken Sie auf den folgenden Link, um fortzufahren:</p>
        <p><a href="{reset_url}">Passwort zurücksetzen</a></p>
        <p>Falls Sie keine Anfrage gestellt haben, können Sie diese E-Mail ignorieren.</p>
        <p>Mit freundlichen Grüßen<br>Ihr PM Tool Team</p>
        """
        try:
            return self.send_email(to_email, subject, content)
        except Exception as e:
            print(f"Failed to send password reset email to {to_email}: {str(e)}")
            return False

    def send_payment_confirmation(
        self,
        to_email: str,
        package_name: str,
        amount: float,
        invoice_path: str
    ) -> bool:
        """Send payment confirmation with invoice"""
        subject = f"Zahlungsbestätigung - {package_name} Paket"
        content = f"""
        <h2>Zahlungsbestätigung</h2>
        <p>Vielen Dank für Ihre Zahlung von €{amount:.2f} für das {package_name} Paket.</p>
        <p>Ihr Abonnement wurde aktiviert. Die Rechnung finden Sie im Anhang dieser E-Mail.</p>
        <p>Mit freundlichen Grüßen<br>Ihr PM Tool Team</p>
        """
        try:
            attachments = [(invoice_path, f"rechnung_{package_name.lower()}.pdf")]
            return self.send_email(to_email, subject, content, attachments)
        except Exception as e:
            print(f"Failed to send payment confirmation to {to_email}: {str(e)}")
            return False

    def send_subscription_expiry_notice(self, to_email: str, days_left: int) -> bool:
        """Send subscription expiry notice"""
        subject = "Ablauf des Abonnements"
        content = f"""
        <h2>Hinweis zum Ablauf des Abonnements</h2>
        <p>Ihr PM Tool Abonnement läuft in {days_left} Tagen ab.</p>
        <p>Um eine unterbrechungsfreie Nutzung zu gewährleisten, erneuern Sie bitte Ihr Abonnement.</p>
        <p><a href="https://pm.bow-agentur.de/subscription">Abonnement verlängern</a></p>
        <p>Mit freundlichen Grüßen<br>Ihr PM Tool Team</p>
        """
        try:
            return self.send_email(to_email, subject, content)
        except Exception as e:
            print(f"Failed to send subscription expiry notice to {to_email}: {str(e)}")
            return False

    def send_subscription_cancellation(self, to_email: str, package_name: str) -> bool:
        """Send subscription cancellation confirmation"""
        subject = "Bestätigung der Abonnement-Kündigung"
        content = f"""
        <h2>Bestätigung der Abonnement-Kündigung</h2>
        <p>Sehr geehrter Kunde,</p>
        <p>wir bestätigen hiermit die Kündigung Ihres Abonnements für das Paket "{package_name}".</p>
        <p>Ihr Zugang bleibt bis zum Ende der aktuellen Abrechnungsperiode aktiv.</p>
        <p>Wir bedauern, dass Sie uns verlassen. Falls Sie Feedback haben, wie wir unseren Service verbessern können, antworten Sie gerne auf diese E-Mail.</p>
        <p>Mit freundlichen Grüßen<br>Ihr PM Tool Team</p>
        """
        try:
            return self.send_email(to_email, subject, content)
        except Exception as e:
            print(f"Failed to send subscription cancellation email to {to_email}: {str(e)}")
            return False
