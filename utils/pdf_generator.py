from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas
import io
import os
from datetime import datetime

class PDFGenerator:
    def __init__(self, invoice_data, settings):
        self.invoice = invoice_data
        self.settings = settings
    
    def generate(self, filename):
        # Create PDF document with custom margins
        doc = SimpleDocTemplate(
            filename, 
            pagesize=A4,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm,
            leftMargin=1.5*cm,
            rightMargin=1.5*cm
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            alignment=TA_CENTER,
            spaceAfter=20,
            textColor=colors.HexColor('#2c3e50')
        )
        
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#7f8c8d')
        )
        
        normal_style = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontSize=10,
            leading=14
        )
        
        bold_style = ParagraphStyle(
            'Bold',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            leading=14
        )
        
        right_style = ParagraphStyle(
            'Right',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_RIGHT
        )
        
        # ==================== HEADER SECTION ====================
        
        # Company Logo and Name
        business_name = self.settings.get('business_name', 'Business Name')
        business_address = self.settings.get('business_address', '')
        business_phone = self.settings.get('business_phone', '')
        business_email = self.settings.get('business_email', '')
        business_gst = self.settings.get('business_gst', '')
        
        # Header Table
        header_data = []
        
        # Company Name
        header_data.append([Paragraph(f"<b>{business_name}</b>", title_style)])
        
        # Address
        if business_address:
            header_data.append([Paragraph(business_address, header_style)])
        
        # Contact Info
        contact_text = ""
        if business_phone:
            contact_text += f"Phone: {business_phone}"
        if business_email:
            if contact_text:
                contact_text += f" | Email: {business_email}"
            else:
                contact_text += f"Email: {business_email}"
        if contact_text:
            header_data.append([Paragraph(contact_text, header_style)])
        
        # GST Number
        if business_gst:
            header_data.append([Paragraph(f"GSTIN: {business_gst}", header_style)])
        
        header_table = Table(header_data, colWidths=[17*cm])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(header_table)
        
        # Horizontal Line
        story.append(Spacer(1, 0.2*inch))
        line_table = Table([['']], colWidths=[17*cm])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, -1), 1, colors.HexColor('#3498db')),
        ]))
        story.append(line_table)
        story.append(Spacer(1, 0.3*inch))
        
        # ==================== INVOICE TITLE ====================
        
        invoice_title_data = [
            [Paragraph("<b>TAX INVOICE</b>", ParagraphStyle('InvoiceTitle', parent=styles['Heading1'], fontSize=18, alignment=TA_CENTER, textColor=colors.HexColor('#2c3e50')))]
        ]
        title_table = Table(invoice_title_data, colWidths=[17*cm])
        title_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(title_table)
        
        # ==================== INVOICE DETAILS ====================
        
        invoice_details_data = [
            [Paragraph(f"<b>Invoice No:</b> {self.invoice['invoice_number']}", normal_style),
             Paragraph(f"<b>Date:</b> {self.invoice['invoice_date'][:10]}", right_style)],
            [Paragraph(f"<b>Due Date:</b> {self.invoice.get('due_date', 'N/A')[:10] if self.invoice.get('due_date') else 'N/A'}", normal_style),
             Paragraph(f"<b>Status:</b> {self.invoice.get('status', 'pending').upper()}", right_style)]
        ]
        
        details_table = Table(invoice_details_data, colWidths=[8.5*cm, 8.5*cm])
        details_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(details_table)
        story.append(Spacer(1, 0.2*inch))
        
        # ==================== CUSTOMER DETAILS ====================
        
        customer_name = self.invoice.get('customer_name', 'N/A')
        customer_address = self.invoice.get('address', 'N/A')
        customer_gst = self.invoice.get('gst_number', 'N/A')
        customer_phone = self.invoice.get('phone', 'N/A')
        
        customer_data = [
            [Paragraph("<b>BILL TO:</b>", bold_style)],
            [Paragraph(customer_name, normal_style)],
            [Paragraph(customer_address, normal_style)],
            [Paragraph(f"Phone: {customer_phone}", normal_style)],
            [Paragraph(f"GSTIN: {customer_gst}", normal_style)],
        ]
        
        customer_table = Table(customer_data, colWidths=[17*cm])
        customer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ]))
        story.append(customer_table)
        story.append(Spacer(1, 0.3*inch))
        
        # ==================== ITEMS TABLE ====================
        
        currency = self.settings.get('currency_symbol', '₹')
        
        # Table headers
        table_data = [
            ['Sl. No.', 'Description of Goods/Services', 'HSN/SAC', 'Quantity', 'Unit Price', 'Tax%', 'Amount']
        ]
        
        # Add items
        for idx, item in enumerate(self.invoice['items'], 1):
            tax_rate = item.get('cgst_rate', 0) + item.get('sgst_rate', 0) + item.get('igst_rate', 0)
            quantity = item['quantity']
            quantity_str = str(int(quantity)) if quantity.is_integer() else f"{quantity:.2f}"
            
            table_data.append([
                str(idx),
                Paragraph(item['product_name'], normal_style),
                item.get('hsn_code', ''),
                quantity_str,
                f"{currency}{item['unit_price']:,.2f}",
                f"{tax_rate}%",
                f"{currency}{item['total']:,.2f}"
            ])
        
        # Create table with proper column widths
        col_widths = [1.2*cm, 5.5*cm, 2.2*cm, 1.8*cm, 2.2*cm, 1.5*cm, 2.6*cm]
        items_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Style the table
        items_table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            
            # Body styling
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (3, 1), (6, -1), 'RIGHT'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('LEFTPADDING', (1, 1), (1, -1), 5),
            
            # Grid lines
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        
        story.append(items_table)
        story.append(Spacer(1, 0.3*inch))
        
        # ==================== TAX BREAKDOWN ====================
        
        # Calculate tax totals
        cgst_total = sum(item.get('cgst_amount', 0) for item in self.invoice['items'])
        sgst_total = sum(item.get('sgst_amount', 0) for item in self.invoice['items'])
        igst_total = sum(item.get('igst_amount', 0) for item in self.invoice['items'])
        
        if cgst_total > 0 or sgst_total > 0 or igst_total > 0:
            tax_data = [['<b>Tax Breakdown</b>', '']]
            if cgst_total > 0:
                tax_data.append(['CGST (9%)', f"{currency}{cgst_total:,.2f}"])
            if sgst_total > 0:
                tax_data.append(['SGST (9%)', f"{currency}{sgst_total:,.2f}"])
            if igst_total > 0:
                tax_data.append(['IGST (18%)', f"{currency}{igst_total:,.2f}"])
            
            tax_table = Table(tax_data, colWidths=[12*cm, 5*cm])
            tax_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor('#bdc3c7')),
            ]))
            story.append(tax_table)
            story.append(Spacer(1, 0.2*inch))
        
        # ==================== TOTALS SECTION ====================
        
        subtotal = self.invoice['subtotal']
        tax_total = self.invoice['tax_total']
        grand_total = self.invoice['grand_total']
        paid_amount = self.invoice.get('paid_amount', 0)
        balance_due = grand_total - paid_amount
        
        totals_data = []
        
        # Subtotal
        totals_data.append(['<b>Subtotal:</b>', '', f"{currency}{subtotal:,.2f}"])
        
        # Tax
        totals_data.append(['<b>Tax Total:</b>', '', f"{currency}{tax_total:,.2f}"])
        
        # Paid amount (if any)
        if paid_amount > 0:
            totals_data.append(['<b>Paid Amount:</b>', '', f"{currency}{paid_amount:,.2f}"])
            totals_data.append(['<b>Balance Due:</b>', '', f"{currency}{balance_due:,.2f}"])
        
        # Grand Total
        totals_data.append(['<b>Grand Total:</b>', '', f"<b>{currency}{grand_total:,.2f}</b>"])
        
        totals_table = Table(totals_data, colWidths=[12*cm, 2*cm, 3*cm])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -2), 10),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LINEABOVE', (0, -2), (-1, -2), 0.5, colors.HexColor('#bdc3c7')),
            ('LINEBELOW', (0, -1), (-1, -1), 2, colors.HexColor('#3498db')),
        ]))
        story.append(totals_table)
        story.append(Spacer(1, 0.3*inch))
        
        # ==================== AMOUNT IN WORDS ====================
        
        amount_words = self.number_to_words(grand_total)
        words_data = [[Paragraph(f"<b>Amount in Words:</b> {amount_words}", normal_style)]]
        words_table = Table(words_data, colWidths=[17*cm])
        words_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecf0f1')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ]))
        story.append(words_table)
        story.append(Spacer(1, 0.3*inch))
        
        # ==================== NOTES SECTION ====================
        
        if self.invoice.get('notes'):
            notes_data = [
                [Paragraph("<b>Notes:</b>", bold_style)],
                [Paragraph(self.invoice['notes'], normal_style)]
            ]
            notes_table = Table(notes_data, colWidths=[17*cm])
            notes_table.setStyle(TableStyle([
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ]))
            story.append(notes_table)
            story.append(Spacer(1, 0.2*inch))
        
        # ==================== TERMS & CONDITIONS ====================
        
        terms = self.settings.get('invoice_terms', '')
        if terms:
            terms_data = [
                [Paragraph("<b>Terms & Conditions:</b>", bold_style)],
                [Paragraph(terms, normal_style)]
            ]
            terms_table = Table(terms_data, colWidths=[17*cm])
            terms_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fff9e6')),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#f39c12')),
            ]))
            story.append(terms_table)
            story.append(Spacer(1, 0.3*inch))
        
        # ==================== FOOTER ====================
        
        footer_text = f"This is a computer generated invoice. Generated on {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        footer_data = [[Paragraph(footer_text, header_style)]]
        footer_table = Table(footer_data, colWidths=[17*cm])
        footer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.HexColor('#bdc3c7')),
        ]))
        story.append(footer_table)
        
        # ==================== BUILD PDF ====================
        
        doc.build(story)
        return filename
    
    def number_to_words(self, num):
        """Convert number to words in Indian format"""
        try:
            from num2words import num2words
            # Convert to Indian numbering system
            words = num2words(num, lang='en_IN')
            return words.upper() + " ONLY"
        except ImportError:
            return f"{num:.2f} ONLY"
        except Exception:
            return f"{num:.2f} ONLY"