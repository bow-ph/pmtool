import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from app.services.invoice_service import InvoiceService
from app.models.invoice import Invoice
from app.models.user import User
from app.models.subscription import Subscription
import os

@pytest.fixture
def db_session():
    return MagicMock()

@pytest.fixture
def invoice_service(db_session):
    return InvoiceService(db_session)

@pytest.fixture
def mock_user():
    return User(
        id=1,
        email="test@example.com",
        client_type="company",
        company_name="Test Corp",
        vat_number="DE123456789",
        billing_address="Test Street 1",
        is_active=True
    )

@pytest.fixture
def mock_subscription():
    return Subscription(
        id=1,
        user_id=1,
        mollie_id="sub_test",
        customer_id="cust_test",
        package_id=1,
        status="active",
        amount=119.0,
        interval="3 months"
    )

def test_generate_invoice_number(invoice_service, db_session):
    """Test unique invoice number generation"""
    today = datetime.now()
    db_session.query().filter().count.return_value = 5
    
    invoice_number = invoice_service.generate_invoice_number()
    assert invoice_number.startswith(f"{today.year}-{today.month:02d}-")
    assert invoice_number.endswith("00006")  # Next after 5 existing invoices

def test_create_invoice_from_payment(invoice_service, db_session, mock_user, mock_subscription):
    """Test invoice creation from payment data"""
    payment_data = {
        "amount": {"value": "119.00", "currency": "EUR"},
        "metadata": {
            "user_id": 1,
            "package_name": "Team Package"
        },
        "subscription_id": "sub_test"
    }
    
    db_session.query(User).filter().first.return_value = mock_user
    db_session.query(Subscription).filter().first.return_value = mock_subscription
    
    invoice = invoice_service.create_invoice_from_payment(payment_data)
    
    assert invoice.user_id == mock_user.id
    assert invoice.subscription_id == mock_subscription.id
    assert invoice.total_amount == 119.0
    assert invoice.status == "paid"
    assert invoice.pdf_path.endswith(".pdf")

def test_create_invoice_with_vat(invoice_service, db_session, mock_user, mock_subscription):
    """Test invoice creation with VAT calculation"""
    mock_user.vat_number = "DE123456789"  # German VAT
    payment_data = {
        "amount": {"value": "119.00", "currency": "EUR"},
        "metadata": {
            "user_id": 1,
            "package_name": "Team Package"
        },
        "subscription_id": "sub_test"
    }
    
    db_session.query(User).filter().first.return_value = mock_user
    db_session.query(Subscription).filter().first.return_value = mock_subscription
    
    invoice = invoice_service.create_invoice_from_payment(payment_data)
    
    assert invoice.total_amount == 119.0
    assert invoice.net_amount == 100.0  # 119 / 1.19
    assert invoice.vat_amount == 19.0
    assert invoice.vat_rate == 0.19

def test_create_invoice_without_vat(invoice_service, db_session, mock_user, mock_subscription):
    """Test invoice creation without VAT for non-EU customers"""
    mock_user.vat_number = None
    payment_data = {
        "amount": {"value": "100.00", "currency": "EUR"},
        "metadata": {
            "user_id": 1,
            "package_name": "Team Package"
        },
        "subscription_id": "sub_test"
    }
    
    db_session.query(User).filter().first.return_value = mock_user
    db_session.query(Subscription).filter().first.return_value = mock_subscription
    
    invoice = invoice_service.create_invoice_from_payment(payment_data)
    
    assert invoice.total_amount == 100.0
    assert invoice.net_amount == 100.0
    assert invoice.vat_amount == 0.0
    assert invoice.vat_rate == 0.0

def test_invoice_storage_path(invoice_service, tmp_path):
    """Test invoice storage path creation"""
    storage_path = tmp_path / "invoices"
    invoice_service.STORAGE_PATH = str(storage_path)
    
    invoice = Invoice(
        id=1,
        invoice_number="2024-01-00001",
        user_id=1,
        total_amount=119.0
    )
    
    path = invoice_service.get_storage_path(invoice)
    assert path.startswith(str(storage_path))
    assert "2024/01" in path
    assert path.endswith("2024-01-00001.pdf")

def test_invoice_generation_error_handling(invoice_service, db_session, mock_user, mock_subscription):
    """Test error handling during invoice generation"""
    payment_data = {
        "amount": {"value": "119.00", "currency": "EUR"},
        "metadata": {
            "user_id": 1,
            "package_name": "Team Package"
        },
        "subscription_id": "sub_test"
    }
    
    db_session.query(User).filter().first.return_value = mock_user
    db_session.query(Subscription).filter().first.return_value = mock_subscription
    
    # Mock PDF generation error
    with patch('app.services.pdf_service.generate_invoice_pdf', side_effect=Exception("PDF generation failed")):
        with pytest.raises(Exception) as exc_info:
            invoice_service.create_invoice_from_payment(payment_data)
        assert "PDF generation failed" in str(exc_info.value)
        
        # Verify invoice was not saved
        db_session.add.assert_not_called()
        db_session.commit.assert_not_called()
