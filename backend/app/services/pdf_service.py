from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
import os
from datetime import datetime
from app.models.invoice import Invoice
from app.core.config import settings

def generate_invoice_pdf(invoice: Invoice) -> None:
    """Generate PDF invoice and save it to the specified path"""
    # Ensure directory exists
    os.makedirs(os.path.dirname(invoice.pdf_path), exist_ok=True)
    
    # Create PDF
    c = canvas.Canvas(invoice.pdf_path, pagesize=A4)
    width, height = A4
    
    # Company Logo (if exists)
    logo_path = "app/static/logo.png"
    if os.path.exists(logo_path):
        c.drawImage(logo_path, 2*cm, height-3*cm, width=4*cm, preserveAspectRatio=True)
    
    # Header
    c.setFont("Helvetica-Bold", 24)
    c.drawString(2*cm, height-3*cm, "Rechnung")
    
    # Company Info
    c.setFont("Helvetica", 10)
    y = height - 5*cm
    for line in [
        settings.COMPANY_NAME,
        settings.COMPANY_ADDRESS,
        f"USt-IdNr: {settings.COMPANY_VAT}",
        f"Tel: {settings.COMPANY_PHONE}",
        f"Email: {settings.COMPANY_EMAIL}",
        f"Web: {settings.COMPANY_WEBSITE}"
    ]:
        c.drawString(2*cm, y, line)
        y -= 0.5*cm
    
    # Invoice Details
    c.setFont("Helvetica-Bold", 12)
    y = height - 9*cm
    c.drawString(2*cm, y, f"Rechnungsnummer: {invoice.invoice_number}")
    c.drawString(2*cm, y-0.7*cm, f"Datum: {invoice.issue_date.strftime('%d.%m.%Y')}")
    
    # Amount
    c.setFont("Helvetica-Bold", 14)
    y = height - 12*cm
    net_amount = invoice.total_amount / 1.19  # Assuming 19% VAT
    vat_amount = invoice.total_amount - net_amount
    
    c.drawString(2*cm, y, f"Nettobetrag: €{net_amount:.2f}")
    c.drawString(2*cm, y-0.7*cm, f"MwSt. (19%): €{vat_amount:.2f}")
    c.drawString(2*cm, y-1.4*cm, f"Gesamtbetrag: €{invoice.total_amount:.2f}")
    
    # Payment Information
    c.setFont("Helvetica", 10)
    y = height - 16*cm
    c.drawString(2*cm, y, "Bankverbindung:")
    for line in settings.COMPANY_BANK_INFO.split("\n"):
        y -= 0.5*cm
        c.drawString(2*cm, y, line)
    
    # Footer
    c.setFont("Helvetica", 8)
    footer_text = [
        "Vielen Dank für Ihr Vertrauen!",
        f"{settings.COMPANY_NAME} | {settings.COMPANY_ADDRESS}",
        f"USt-IdNr: {settings.COMPANY_VAT} | Tel: {settings.COMPANY_PHONE} | Email: {settings.COMPANY_EMAIL}"
    ]
    y = 2*cm
    for line in footer_text:
        c.drawString(2*cm, y, line)
        y -= 0.4*cm
    
    c.save()
