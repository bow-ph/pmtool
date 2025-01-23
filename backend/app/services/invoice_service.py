from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
import os
from app.models.invoice import Invoice
from app.models.user import User
from app.models.subscription import Subscription
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os

class InvoiceService:
    def __init__(self, db: Session):
        self.db = db
        # Set up invoice directory based on environment
        if os.getenv('TESTING', 'false').lower() == 'true':
            self.invoice_dir = "/tmp/test_invoices"
        else:
            self.invoice_dir = "/var/lib/pmtool/invoices"
        os.makedirs(self.invoice_dir, exist_ok=True)

    def generate_invoice_number(self) -> str:
        """Generate a unique invoice number"""
        year = datetime.now().year
        # Get the latest invoice number for this year
        latest_invoice = (
            self.db.query(Invoice)
            .filter(Invoice.invoice_number.like(f"INV-{year}-%"))
            .order_by(Invoice.invoice_number.desc())
            .first()
        )

        if latest_invoice:
            # Extract the sequence number and increment
            sequence = int(latest_invoice.invoice_number.split("-")[-1]) + 1
        else:
            sequence = 1

        return f"INV-{year}-{sequence:04d}"

    def create_invoice(
        self,
        user_id: int,
        subscription_id: int,
        total_amount: float,
        net_amount: float,
        vat_amount: float,
        vat_rate: float,
        description: str,
        currency: str = "EUR",
        issue_date: Optional[datetime] = None
    ) -> Invoice:
        """Create a new invoice record and generate PDF"""
        # Get user and subscription details
        user = self.db.query(User).filter(User.id == user_id).first()
        subscription = self.db.query(Subscription).filter(Subscription.id == subscription_id).first()

        if not user or not subscription:
            raise ValueError("User or subscription not found")

        # Generate invoice number
        invoice_number = self.generate_invoice_number()

        # Create invoice record
        invoice = Invoice(
            invoice_number=invoice_number,
            user_id=user_id,
            subscription_id=subscription_id,
            total_amount=total_amount,
            net_amount=net_amount,
            vat_amount=vat_amount,
            vat_rate=vat_rate,
            currency=currency,
            status="pending",
            issue_date=issue_date or datetime.utcnow()
        )
        self.db.add(invoice)
        self.db.flush()  # Get the ID without committing

        # Generate PDF
        pdf_path = self._generate_pdf(invoice, user, subscription, description)
        invoice.pdf_path = pdf_path
        invoice.status = "paid"  # Update status since this is called after payment

        self.db.commit()
        return invoice

    def _generate_pdf(
        self,
        invoice: Invoice,
        user: User,
        subscription: Subscription,
        description: str
    ) -> str:
        """Generate PDF invoice and return the file path"""
        pdf_path = os.path.join(self.invoice_dir, f"{invoice.invoice_number}.pdf")
        
        # Create PDF
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4

        # Header
        c.setFont("Helvetica-Bold", 24)
        c.drawString(50, height - 50, "Rechnung")
        
        # Invoice details
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 100, f"Rechnungsnummer: {invoice.invoice_number}")
        c.drawString(50, height - 120, f"Datum: {invoice.issue_date.strftime('%d.%m.%Y')}")
        
        # Company details
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 160, "BOW Agentur")
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 180, "Musterstraße 123")
        c.drawString(50, height - 200, "12345 Musterstadt")
        c.drawString(50, height - 220, "Deutschland")
        
        # Customer details
        y = height - 280
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Rechnungsempfänger:")
        c.setFont("Helvetica", 12)
        y -= 20
        if user.client_type == "company":
            c.drawString(50, y, user.company_name)
            y -= 20
            if user.contact_person:
                c.drawString(50, y, f"z.Hd. {user.contact_person}")
                y -= 20
        else:
            c.drawString(50, y, user.email)
            y -= 20
        
        if user.billing_address:
            for line in user.billing_address.split("\n"):
                c.drawString(50, y, line)
                y -= 20
        
        # Invoice items
        y = height - 400
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Beschreibung")
        c.drawString(350, y, "Nettobetrag")
        c.drawString(450, y, "MwSt.")
        c.drawString(500, y, "Gesamt")
        y -= 30
        
        c.setFont("Helvetica", 12)
        c.drawString(50, y, description)
        c.drawRightString(400, y, f"{invoice.currency} {invoice.net_amount:.2f}")
        if invoice.vat_rate > 0:
            c.drawRightString(475, y, f"{invoice.vat_amount:.2f}")
            c.drawString(425, y + 15, f"({invoice.vat_rate * 100:.0f}%)")
        else:
            c.drawRightString(475, y, "0.00")
            c.drawString(425, y + 15, "(0%)")
        c.drawRightString(550, y, f"{invoice.currency} {invoice.total_amount:.2f}")
        
        # Total
        y -= 40
        c.setFont("Helvetica-Bold", 12)
        c.drawString(350, y, "Nettobetrag:")
        c.drawRightString(500, y, f"{invoice.currency} {invoice.net_amount:.2f}")
        
        if invoice.vat_rate > 0:
            y -= 20
            c.drawString(350, y, f"MwSt. ({invoice.vat_rate * 100:.0f}%):")
            c.drawRightString(500, y, f"{invoice.currency} {invoice.vat_amount:.2f}")
        
        y -= 30
        c.setFont("Helvetica-Bold", 14)
        c.drawString(350, y, "Gesamtbetrag:")
        c.drawRightString(500, y, f"{invoice.currency} {invoice.total_amount:.2f}")
        
        # Footer
        c.setFont("Helvetica", 10)
        c.drawString(50, 50, "Vielen Dank für Ihr Vertrauen!")
        
        c.save()
        return pdf_path

    def get_invoice_path(self, invoice_number: str) -> Optional[str]:
        """Get the path to an invoice PDF"""
        invoice = (
            self.db.query(Invoice)
            .filter(Invoice.invoice_number == invoice_number)
            .first()
        )
        return invoice.pdf_path if invoice else None
