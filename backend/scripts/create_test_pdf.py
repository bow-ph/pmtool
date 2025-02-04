from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

c = canvas.Canvas('test.pdf', pagesize=letter)
c.drawString(100, 750, 'Test Project Proposal')
c.drawString(100, 730, 'Tasks:')
c.drawString(120, 710, '1. Setup Development Environment - 4 hours')
c.drawString(120, 690, '2. Implement User Authentication - 8 hours')
c.drawString(120, 670, '3. Create Database Schema - 6 hours')
c.save()
