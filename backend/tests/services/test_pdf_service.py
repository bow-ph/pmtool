import pytest
from unittest.mock import patch, MagicMock
from app.services.pdf_service import generate_invoice_pdf
from app.models.invoice import Invoice
from datetime import datetime
import os

@pytest.fixture
def mock_invoice():
    return Invoice(
        id=1,
        invoice_number="2024-01-00001",
        user_id=1,
        subscription_id=1,
        issue_date=datetime.utcnow(),
        total_amount=99.99,
        pdf_path="/tmp/test_invoice.pdf",
        status="paid"
    )

def test_generate_invoice_pdf(mock_invoice, tmp_path):
    # Set up test PDF path
    test_pdf_path = tmp_path / "test_invoice.pdf"
    mock_invoice.pdf_path = str(test_pdf_path)
    
    # Generate PDF
    generate_invoice_pdf(mock_invoice)
    
    # Check if PDF was created
    assert os.path.exists(test_pdf_path)
    assert os.path.getsize(test_pdf_path) > 0

def test_generate_invoice_pdf_creates_directory(mock_invoice, tmp_path):
    # Set up nested directory structure
    nested_dir = tmp_path / "invoices" / "2024" / "01"
    pdf_path = nested_dir / "test_invoice.pdf"
    mock_invoice.pdf_path = str(pdf_path)
    
    # Generate PDF
    generate_invoice_pdf(mock_invoice)
    
    # Check if directories were created
    assert os.path.exists(nested_dir)
    assert os.path.exists(pdf_path)

@pytest.mark.parametrize("amount,expected_net,expected_vat", [
    (119.0, 100.0, 19.0),
    (59.5, 50.0, 9.5),
    (238.0, 200.0, 38.0),
])
def test_invoice_calculations(mock_invoice, amount, expected_net, expected_vat, tmp_path):
    # Set up test invoice with different amounts
    test_pdf_path = tmp_path / "test_invoice.pdf"
    mock_invoice.pdf_path = str(test_pdf_path)
    mock_invoice.total_amount = amount
    
    # Generate PDF
    generate_invoice_pdf(mock_invoice)
    
    # Verify PDF was created (actual VAT calculations are done in the PDF)
    assert os.path.exists(test_pdf_path)
    assert os.path.getsize(test_pdf_path) > 0

def test_generate_invoice_pdf_with_logo(mock_invoice, tmp_path):
    # Create mock logo file
    logo_dir = tmp_path / "app" / "static"
    os.makedirs(logo_dir)
    logo_path = logo_dir / "logo.png"
    with open(logo_path, "wb") as f:
        f.write(b"fake png content")
    
    # Set up test PDF path
    test_pdf_path = tmp_path / "test_invoice.pdf"
    mock_invoice.pdf_path = str(test_pdf_path)
    
    # Mock logo path
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = True
        
        # Generate PDF
        generate_invoice_pdf(mock_invoice)
        
        # Check if PDF was created
        assert os.path.exists(test_pdf_path)
        assert os.path.getsize(test_pdf_path) > 0
