import pytest
from unittest.mock import patch, MagicMock
from app.services.email_service import EmailService
from sendgrid.helpers.mail import Mail

@pytest.fixture
def email_service():
    with patch.dict('os.environ', {
        'SENDGRID_API_KEY': 'test_key',
        'SMTP_FROM_EMAIL': 'test@example.com',
        'SMTP_FROM_NAME': 'Test Sender'
    }):
        return EmailService()

def test_send_welcome_email(email_service):
    """Test sending welcome email in German"""
    with patch.object(email_service.client, 'send') as mock_send:
        result = email_service.send_welcome_email("test@example.com", "Max Mustermann")
        assert result is True
        
        # Verify email content
        call_args = mock_send.call_args[0][0]
        assert isinstance(call_args, Mail)
        assert "Willkommen bei PM Tool" in call_args.subject
        assert "Sehr geehrte(r) Max Mustermann" in call_args.html_content
        assert "Projekte erstellen und verwalten" in call_args.html_content
        assert "Mit freundlichen Grüßen" in call_args.html_content

def test_send_password_reset_email(email_service):
    """Test sending password reset email in German"""
    with patch.object(email_service.client, 'send') as mock_send:
        result = email_service.send_password_reset_email("test@example.com", "test-token")
        assert result is True
        
        call_args = mock_send.call_args[0][0]
        assert isinstance(call_args, Mail)
        assert "PM Tool Passwort zurücksetzen" in call_args.subject
        assert "Passwort zurücksetzen" in call_args.html_content
        assert "Mit freundlichen Grüßen" in call_args.html_content

def test_send_payment_confirmation(email_service):
    """Test sending payment confirmation email in German"""
    with patch.object(email_service.client, 'send') as mock_send:
        with patch('builtins.open', MagicMock()):
            result = email_service.send_payment_confirmation(
                "test@example.com",
                "Team Paket",
                99.99,
                "/tmp/test-invoice.pdf"
            )
            assert result is True
            
            call_args = mock_send.call_args[0][0]
            assert isinstance(call_args, Mail)
            assert "Zahlungsbestätigung - Team Paket" in call_args.subject
            assert "€99.99" in call_args.html_content
            assert "Ihr Abonnement wurde aktiviert" in call_args.html_content
            assert call_args.attachment is not None

def test_send_subscription_expiry_notice(email_service):
    """Test sending subscription expiry notice in German"""
    with patch.object(email_service.client, 'send') as mock_send:
        result = email_service.send_subscription_expiry_notice("test@example.com", 7)
        assert result is True
        
        call_args = mock_send.call_args[0][0]
        assert isinstance(call_args, Mail)
        assert "Ablauf des Abonnements" in call_args.subject
        assert "7 Tagen" in call_args.html_content
        assert "Abonnement verlängern" in call_args.html_content

def test_email_error_handling(email_service):
    """Test error handling in email sending"""
    with patch.object(email_service.client, 'send', side_effect=Exception("Test error")):
        result = email_service.send_welcome_email("test@example.com", "Test User")
        assert result is False

def test_attachment_handling(email_service):
    """Test handling of email attachments"""
    mock_file_content = b"test content"
    mock_file = MagicMock()
    mock_file.__enter__.return_value.read.return_value = mock_file_content
    
    with patch('builtins.open', return_value=mock_file):
        with patch.object(email_service.client, 'send') as mock_send:
            result = email_service.send_payment_confirmation(
                "test@example.com",
                "Test Package",
                99.99,
                "/tmp/test-invoice.pdf"
            )
            assert result is True
            
            call_args = mock_send.call_args[0][0]
            assert call_args.attachment is not None
            assert call_args.attachment.file_content is not None
            assert call_args.attachment.filename == "rechnung_test_package.pdf"
