from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import io
import base64

class PDFGenerator:
    def __init__(self, invoice_data, settings):
        self.invoice = invoice_data
        self.settings = settings
    
    def generate(self, filename):
        doc = SimpleDocTemplate(filename, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, alignment=TA_CENTER)
        header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=10)
        
        # Header with logo and business info
        if self.settings.get('company_logo'):
            try:
                logo_data = base64.b64decode(self.settings['company_logo'])
                logo = Image(io.BytesIO(logo_data), width=1*inch, height=1*inch)
                story.append(logo)
            except:
                pass
        
        # Business details
        business_name = self.settings.get('business_name', 'Business Name')
        story.append(Paragraph(f"<b>{business_name}</b>", title_style))
        story.append(Paragraph(self.settings.get('business_address', ''), header_style))
        story.append(Paragraph(f"Phone: {self.settings.get('business_phone', '')}", header_style))
        story.append(Paragraph(f"Email: {self.settings.get('business_email', '')}", header_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Invoice title
        story.append(Paragraph(f"<b>INVOICE</b>", title_style))
        story.append(Paragraph(f"Invoice #: {self.invoice['invoice_number']}", header_style))
        story.append(Paragraph(f"Date: {self.invoice['invoice_date'][:10]}", header_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Customer details
        story.append(Paragraph("<b>Bill To:</b>", styles['Normal']))
        story.append(Paragraph(self.invoice.get('customer_name', ''), header_style))
        story.append(Paragraph(self.invoice.get('address', ''), header_style))
        story.append(Paragraph(f"Phone: {self.invoice.get('phone', '')}", header_style))
        story.append(Paragraph(f"GST: {self.invoice.get('gst_number', '')}", header_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Items table
        data = [['Item', 'Description', 'Quantity', 'Unit Price', 'Tax', 'Total']]
        for item in self.invoice['items']:
            data.append([
                item['product_name'],
                item.get('description', '')[:50],
                str(item['quantity']),
                f"{self.settings.get('currency_symbol', '$')}{item['unit_price']:.2f}",
                f"{item['tax_rate']}%",
                f"{self.settings.get('currency_symbol', '$')}{item['total']:.2f}"
            ])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        # Totals
        currency = self.settings.get('currency_symbol', '$')
        story.append(Paragraph(f"<b>Subtotal: {currency}{self.invoice['subtotal']:.2f}</b>", styles['Normal']))
        story.append(Paragraph(f"<b>Tax ({self.settings.get('gst_percentage', '0')}%): {currency}{self.invoice['tax_total']:.2f}</b>", styles['Normal']))
        story.append(Paragraph(f"<b>Grand Total: {currency}{self.invoice['grand_total']:.2f}</b>", styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))
        
        # Terms
        story.append(Paragraph("<b>Terms & Conditions:</b>", styles['Normal']))
        story.append(Paragraph(self.settings.get('invoice_terms', ''), header_style))
        
        # Build PDF
        doc.build(story)