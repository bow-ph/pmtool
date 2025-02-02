from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

c = canvas.Canvas('test.pdf', pagesize=letter)
c.drawString(100, 750, 'Test Project Document')
c.drawString(100, 700, 'Tasks:')
c.drawString(120, 680, '1. Design user interface')
c.drawString(120, 660, '2. Implement backend API')
c.drawString(120, 640, '3. Test integration')
c.save()
