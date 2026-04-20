from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import io
import os
from datetime import datetime

class PDFGenerator:
    def __init__(self, invoice_data, settings):
        self.invoice = invoice_data
        self.settings = settings
    
    def generate(self, filename):
        doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=1*cm, bottomMargin=1*cm)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, alignment=TA_CENTER, spaceAfter=20)
        header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER)
        normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=9)
        bold_style = ParagraphStyle('Bold', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold')
        
        # Header with business info
        business_name = self.settings.get('business_name', 'Business Name')
        business_address = self.settings.get('business_address', '')
        business_phone = self.settings.get('business_phone', '')
        business_email = self.settings.get('business_email', '')
        business_gst = self.settings.get('business_gst', '')
        
        # Business Header
        header_data = [
            [Paragraph(f"<b>{business_name}</b>", title_style)],
            [Paragraph(business_address, header_style)],
            [Paragraph(f"Phone: {business_phone} | Email: {business_email}", header_style)],
            [Paragraph(f"GSTIN: {business_gst}", header_style)]
        ]
        header_table = Table(header_data, colWidths=[17*cm])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Invoice Title
        invoice_title = f"TAX INVOICE"
        story.append(Paragraph(f"<b>{invoice_title}</b>", title_style))
        
        # Invoice Details
        invoice_details_data = [
            [Paragraph(f"<b>Invoice No:</b> {self.invoice['invoice_number']}", normal_style),
             Paragraph(f"<b>Date:</b> {self.invoice['invoice_date'][:10]}", normal_style)],
            [Paragraph(f"<b>Due Date:</b> {self.invoice.get('due_date', 'N/A')[:10] if self.invoice.get('due_date') else 'N/A'}", normal_style),
             Paragraph(f"<b>Status:</b> {self.invoice.get('status', 'pending').upper()}", normal_style)]
        ]
        details_table = Table(invoice_details_data, colWidths=[8.5*cm, 8.5*cm])
        details_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        story.append(details_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Customer Details
        customer_name = self.invoice.get('customer_name', 'N/A')
        customer_address = self.invoice.get('address', 'N/A')
        customer_gst = self.invoice.get('gst_number', 'N/A')
        
        customer_data = [
            [Paragraph("<b>Bill To:</b>", bold_style)],
            [Paragraph(customer_name, normal_style)],
            [Paragraph(customer_address, normal_style)],
            [Paragraph(f"GSTIN: {customer_gst}", normal_style)]
        ]
        customer_table = Table(customer_data, colWidths=[17*cm])
        customer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ]))
        story.append(customer_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Items Table
        currency = self.settings.get('currency_symbol', '₹')
        table_data = [['S.No', 'Description', 'HSN/SAC', 'Quantity', 'Unit Price', 'Tax%', 'Amount']]
        
        for idx, item in enumerate(self.invoice['items'], 1):
            tax_rate = item.get('cgst_rate', 0) + item.get('sgst_rate', 0) + item.get('igst_rate', 0)
            table_data.append([
                str(idx),
                item['product_name'],
                item.get('hsn_code', ''),
                str(int(item['quantity'])) if item['quantity'].is_integer() else str(item['quantity']),
                f"{currency}{item['unit_price']:.2f}",
                f"{tax_rate}%",
                f"{currency}{item['total']:.2f}"
            ])
        
        items_table = Table(table_data, colWidths=[1*cm, 5*cm, 2.5*cm, 1.5*cm, 2*cm, 1.5*cm, 2.5*cm])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Totals
        subtotal = self.invoice['subtotal']
        tax_total = self.invoice['tax_total']
        grand_total = self.invoice['grand_total']
        
        totals_data = [
            ['', '', f"Subtotal:", f"{currency}{subtotal:.2f}"],
            ['', '', f"Tax Total:", f"{currency}{tax_total:.2f}"],
            ['', '', f"<b>Grand Total:</b>", f"<b>{currency}{grand_total:.2f}</b>"]
        ]
        totals_table = Table(totals_data, colWidths=[10*cm, 2*cm, 3*cm, 3*cm])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('FONTNAME', (2, 2), (3, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        story.append(totals_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Amount in words
        amount_in_words = self.number_to_words(grand_total)
        story.append(Paragraph(f"<b>Amount in Words:</b> {amount_in_words}", normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Notes
        if self.invoice.get('notes'):
            story.append(Paragraph(f"<b>Notes:</b> {self.invoice['notes']}", normal_style))
            story.append(Spacer(1, 0.2*inch))
        
        # Terms
        terms = self.settings.get('invoice_terms', '')
        if terms:
            story.append(Paragraph(f"<b>Terms & Conditions:</b>", bold_style))
            story.append(Paragraph(terms, normal_style))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        footer_text = f"This is a computer generated invoice. Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        story.append(Paragraph(footer_text, header_style))
        
        # Build PDF
        doc.build(story)
        return filename
    
    def number_to_words(self, num):
        """Convert number to words"""
        try:
            from num2words import num2words
            return num2words(num, lang='en_IN').upper() + " ONLY"
        except:
            return f"{num:.2f} ONLY"