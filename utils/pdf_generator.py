from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas
import io
import os
import base64
from datetime import datetime
import traceback

class PDFGenerator:
    def __init__(self, invoice_data, settings):
        self.invoice = invoice_data
        self.settings = settings
    
    def generate(self, filename):
        """Generate PDF with comprehensive error handling"""
        try:
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
                spaceAfter=10,
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
            
            # ==================== HEADER SECTION WITH LOGO ====================
            try:
                business_name = self.settings.get('business_name', 'Business Name')
                business_address = self.settings.get('business_address', '')
                business_phone = self.settings.get('business_phone', '')
                business_email = self.settings.get('business_email', '')
                business_gst = self.settings.get('business_gst', '')
                business_website = self.settings.get('business_website', '')
                
                # Check for logo
                logo_data = self.settings.get('company_logo', '')
                has_logo = logo_data and len(logo_data) > 0 and logo_data != "None"
                
                # Header with Logo
                if has_logo:
                    try:
                        # Decode and create logo image
                        logo_bytes = base64.b64decode(logo_data)
                        logo_buffer = io.BytesIO(logo_bytes)
                        logo = Image(logo_buffer, width=1.2*inch, height=1.2*inch)
                        
                        # Create header with logo and business info
                        header_data = [
                            [logo, Paragraph(f"<b>{self.escape_xml(business_name)}</b>", title_style)]
                        ]
                        header_table = Table(header_data, colWidths=[2.5*cm, 14.5*cm])
                        header_table.setStyle(TableStyle([
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                        ]))
                        story.append(header_table)
                    except Exception as e:
                        print(f"Error loading logo: {e}")
                        story.append(Paragraph(f"<b>{self.escape_xml(business_name)}</b>", title_style))
                else:
                    story.append(Paragraph(f"<b>{self.escape_xml(business_name)}</b>", title_style))
                
                # Business Address and Contact
                contact_lines = []
                if business_address:
                    contact_lines.append(self.escape_xml(business_address))
                contact_info = ""
                if business_phone:
                    contact_info += f"Phone: {self.escape_xml(business_phone)}"
                if business_email:
                    if contact_info:
                        contact_info += f" | Email: {self.escape_xml(business_email)}"
                    else:
                        contact_info += f"Email: {self.escape_xml(business_email)}"
                if business_website:
                    if contact_info:
                        contact_info += f" | Web: {self.escape_xml(business_website)}"
                    else:
                        contact_info += f"Web: {self.escape_xml(business_website)}"
                
                if contact_info:
                    contact_lines.append(contact_info)
                if business_gst:
                    contact_lines.append(f"GSTIN: {self.escape_xml(business_gst)}")
                
                for line in contact_lines:
                    story.append(Paragraph(line, header_style))
                
                # Horizontal Line
                story.append(Spacer(1, 0.2*inch))
                line_table = Table([['']], colWidths=[17*cm])
                line_table.setStyle(TableStyle([
                    ('LINEABOVE', (0, 0), (-1, -1), 1.5, colors.HexColor('#3498db')),
                ]))
                story.append(line_table)
                story.append(Spacer(1, 0.3*inch))
                
            except Exception as e:
                print(f"Error in header section: {e}")
                traceback.print_exc()
                story.append(Paragraph("Business Name", title_style))
                story.append(Spacer(1, 0.3*inch))
            
            # ==================== INVOICE TITLE ====================
            try:
                invoice_title_data = [
                    [Paragraph("<b>TAX INVOICE</b>", ParagraphStyle('InvoiceTitle', parent=styles['Heading1'], fontSize=18, alignment=TA_CENTER, textColor=colors.HexColor('#2c3e50')))]
                ]
                title_table = Table(invoice_title_data, colWidths=[17*cm])
                title_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ]))
                story.append(title_table)
            except Exception as e:
                print(f"Error in invoice title: {e}")
            
            # ==================== INVOICE DETAILS ====================
            try:
                invoice_number = self.escape_xml(self.invoice.get('invoice_number', 'N/A'))
                invoice_date = self.invoice.get('invoice_date', '')
                if invoice_date and len(invoice_date) > 10:
                    invoice_date = invoice_date[:10]
                due_date = self.invoice.get('due_date', 'N/A')
                if due_date and due_date != 'N/A' and len(due_date) > 10:
                    due_date = due_date[:10]
                status = self.escape_xml(self.invoice.get('status', 'pending').upper())
                
                invoice_details_data = [
                    [Paragraph(f"<b>Invoice No:</b> {invoice_number}", normal_style),
                     Paragraph(f"<b>Date:</b> {invoice_date}", right_style)],
                    [Paragraph(f"<b>Due Date:</b> {due_date}", normal_style),
                     Paragraph(f"<b>Status:</b> {status}", right_style)]
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
            except Exception as e:
                print(f"Error in invoice details: {e}")
                traceback.print_exc()
            
            # ==================== CUSTOMER DETAILS ====================
            try:
                customer_name = self.escape_xml(self.invoice.get('customer_name', 'N/A'))
                customer_address = self.escape_xml(self.invoice.get('address', 'N/A'))
                customer_gst = self.escape_xml(self.invoice.get('gst_number', 'N/A'))
                customer_phone = self.escape_xml(self.invoice.get('phone', 'N/A'))
                
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
            except Exception as e:
                print(f"Error in customer details: {e}")
                traceback.print_exc()
            
            # ==================== ITEMS TABLE ====================
            try:
                currency = self.settings.get('currency_symbol', '₹')
                
                # Table headers
                table_data = [
                    ['Sl. No.', 'Description of Goods/Services', 'HSN/SAC', 'Quantity', 'Unit Price', 'Tax%', 'Amount']
                ]
                
                # Add items
                for idx, item in enumerate(self.invoice.get('items', []), 1):
                    try:
                        tax_rate = item.get('cgst_rate', 0) + item.get('sgst_rate', 0) + item.get('igst_rate', 0)
                        quantity = item.get('quantity', 0)
                        if isinstance(quantity, (int, float)):
                            quantity_str = str(int(quantity)) if quantity.is_integer() else f"{quantity:.2f}"
                        else:
                            quantity_str = str(quantity)
                        
                        product_name = self.escape_xml(item.get('product_name', 'N/A'))
                        hsn_code = self.escape_xml(item.get('hsn_code', ''))
                        unit_price = item.get('unit_price', 0)
                        total = item.get('total', 0)
                        
                        table_data.append([
                            str(idx),
                            Paragraph(product_name, normal_style),
                            hsn_code,
                            quantity_str,
                            f"{currency}{unit_price:,.2f}",
                            f"{tax_rate}%",
                            f"{currency}{total:,.2f}"
                        ])
                    except Exception as e:
                        print(f"Error processing item {idx}: {e}")
                        continue
                
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
            except Exception as e:
                print(f"Error in items table: {e}")
                traceback.print_exc()
                story.append(Paragraph("Error loading items", normal_style))
                story.append(Spacer(1, 0.3*inch))
            
            # ==================== TAX BREAKDOWN ====================
            try:
                # Calculate tax totals
                cgst_total = sum(item.get('cgst_amount', 0) for item in self.invoice.get('items', []))
                sgst_total = sum(item.get('sgst_amount', 0) for item in self.invoice.get('items', []))
                igst_total = sum(item.get('igst_amount', 0) for item in self.invoice.get('items', []))
                
                if cgst_total > 0 or sgst_total > 0 or igst_total > 0:
                    currency = self.settings.get('currency_symbol', '₹')
                    tax_data = [['<b>Tax Breakdown</b>', '', 'Amount']]
                    if cgst_total > 0:
                        tax_data.append(['CGST', f"@{self.settings.get('default_cgst', '9')}%", f"{currency}{cgst_total:,.2f}"])
                    if sgst_total > 0:
                        tax_data.append(['SGST', f"@{self.settings.get('default_sgst', '9')}%", f"{currency}{sgst_total:,.2f}"])
                    if igst_total > 0:
                        tax_data.append(['IGST', f"@{self.settings.get('default_igst', '18')}%", f"{currency}{igst_total:,.2f}"])
                    
                    tax_table = Table(tax_data, colWidths=[8*cm, 4*cm, 5*cm])
                    tax_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                        ('ALIGN', (1, 0), (2, -1), 'RIGHT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 11),
                        ('FONTSIZE', (0, 1), (-1, -1), 10),
                        ('TOPPADDING', (0, 0), (-1, -1), 5),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor('#bdc3c7')),
                        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                    ]))
                    story.append(tax_table)
                    story.append(Spacer(1, 0.2*inch))
            except Exception as e:
                print(f"Error in tax breakdown: {e}")
            
            # ==================== TOTALS SECTION ====================
            try:
                currency = self.settings.get('currency_symbol', '₹')
                subtotal = self.invoice.get('subtotal', 0)
                tax_total = self.invoice.get('tax_total', 0)
                grand_total = self.invoice.get('grand_total', 0)
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
            except Exception as e:
                print(f"Error in totals section: {e}")
                traceback.print_exc()
            
            # ==================== AMOUNT IN WORDS ====================
            try:
                grand_total = self.invoice.get('grand_total', 0)
                amount_words = self.number_to_words(grand_total)
                words_data = [[Paragraph(f"<b>Amount in Words:</b> {self.escape_xml(amount_words)}", normal_style)]]
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
            except Exception as e:
                print(f"Error in amount words: {e}")
            
            # ==================== BANK DETAILS SECTION ====================
            try:
                bank_name = self.settings.get('bank_name', '')
                bank_account_name = self.settings.get('bank_account_name', '')
                bank_account_number = self.settings.get('bank_account_number', '')
                bank_ifsc = self.settings.get('bank_ifsc', '')
                bank_branch = self.settings.get('bank_branch', '')
                bank_upi_id = self.settings.get('bank_upi_id', '')
                
                if bank_name or bank_account_number:
                    bank_data = [
                        [Paragraph("<b>BANK DETAILS FOR PAYMENT</b>", bold_style)],
                    ]
                    
                    if bank_name:
                        bank_data.append([Paragraph(f"<b>Bank:</b> {self.escape_xml(bank_name)}", normal_style)])
                    if bank_account_name:
                        bank_data.append([Paragraph(f"<b>Account Name:</b> {self.escape_xml(bank_account_name)}", normal_style)])
                    if bank_account_number:
                        bank_data.append([Paragraph(f"<b>Account Number:</b> {self.escape_xml(bank_account_number)}", normal_style)])
                    if bank_ifsc:
                        bank_data.append([Paragraph(f"<b>IFSC Code:</b> {self.escape_xml(bank_ifsc)}", normal_style)])
                    if bank_branch:
                        bank_data.append([Paragraph(f"<b>Branch:</b> {self.escape_xml(bank_branch)}", normal_style)])
                    if bank_upi_id:
                        bank_data.append([Paragraph(f"<b>UPI ID:</b> {self.escape_xml(bank_upi_id)}", normal_style)])
                    
                    bank_table = Table(bank_data, colWidths=[17*cm])
                    bank_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ('LEFTPADDING', (0, 0), (-1, -1), 10),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#3498db')),
                    ]))
                    story.append(bank_table)
                    story.append(Spacer(1, 0.2*inch))
            except Exception as e:
                print(f"Error in bank details: {e}")
            
            # ==================== NOTES SECTION ====================
            try:
                if self.invoice.get('notes'):
                    notes_text = self.escape_xml(self.invoice['notes'])
                    notes_data = [
                        [Paragraph("<b>Notes:</b>", bold_style)],
                        [Paragraph(notes_text, normal_style)]
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
            except Exception as e:
                print(f"Error in notes section: {e}")
            
            # ==================== TERMS & CONDITIONS ====================
            try:
                terms = self.settings.get('invoice_terms', '')
                if terms:
                    terms_text = self.escape_xml(terms)
                    terms_data = [
                        [Paragraph("<b>Terms & Conditions:</b>", bold_style)],
                        [Paragraph(terms_text, normal_style)]
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
            except Exception as e:
                print(f"Error in terms section: {e}")
            
            # ==================== FOOTER ====================
            try:
                footer_text = f"This is a computer generated invoice. Generated on {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
                footer_data = [[Paragraph(footer_text, header_style)]]
                footer_table = Table(footer_data, colWidths=[17*cm])
                footer_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('TOPPADDING', (0, 0), (-1, -1), 10),
                    ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.HexColor('#bdc3c7')),
                ]))
                story.append(footer_table)
            except Exception as e:
                print(f"Error in footer: {e}")
            
            # ==================== BUILD PDF ====================
            doc.build(story)
            return filename
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            traceback.print_exc()
            raise Exception(f"Failed to generate PDF: {str(e)}")
    
    def escape_xml(self, text):
        """Escape XML special characters for ReportLab"""
        if not text:
            return ""
        text = str(text)
        # Replace XML special characters
        replacements = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&apos;'
        }
        for char, escape in replacements.items():
            text = text.replace(char, escape)
        return text
    
    def number_to_words(self, num):
        """Convert number to words in Indian format with safe fallback"""
        try:
            # Try to import num2words
            try:
                from num2words import num2words
                # Convert to Indian numbering system
                words = num2words(num, lang='en_IN')
                return f"{words.upper()} ONLY"
            except ImportError:
                # Fallback to simple number formatting
                return f"{num:,.2f} ONLY"
            except Exception as e:
                print(f"Error in num2words: {e}")
                return f"{num:,.2f} ONLY"
        except Exception:
            return f"{num:,.2f} ONLY"