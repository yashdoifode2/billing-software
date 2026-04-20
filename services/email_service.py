import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from database.db_manager import DatabaseManager

class EmailService:
    def __init__(self):
        self.db = DatabaseManager()
        self.load_settings()
    
    def load_settings(self):
        """Load SMTP settings from database"""
        settings = self.db.fetch_all("SELECT setting_key, setting_value FROM settings")
        self.settings = {s['setting_key']: s['setting_value'] for s in settings}
    
    def send_email(self, to_email, subject, body, attachment_path=None):
        """Send email with optional attachment"""
        try:
            smtp_host = self.settings.get('smtp_host', '')
            smtp_port = int(self.settings.get('smtp_port', 587))
            smtp_user = self.settings.get('smtp_user', '')
            smtp_password = self.settings.get('smtp_password', '')
            from_email = self.settings.get('smtp_from_email', smtp_user)
            use_tls = self.settings.get('smtp_use_tls', '1') == '1'
            
            if not smtp_host or not smtp_user or not smtp_password:
                return False, "SMTP settings not configured. Please configure email settings first."
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Email body (HTML)
            msg.attach(MIMEText(body, 'html'))
            
            # Attach file if provided
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(attachment_path)}"')
                    msg.attach(part)
            
            # Send email
            if use_tls:
                server = smtplib.SMTP(smtp_host, smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(smtp_host, smtp_port)
            
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()
            
            return True, "Email sent successfully"
        
        except smtplib.SMTPAuthenticationError:
            return False, "SMTP Authentication failed. Please check your username and password."
        except smtplib.SMTPException as e:
            return False, f"SMTP Error: {str(e)}"
        except Exception as e:
            return False, f"Failed to send email: {str(e)}"
    
    def send_invoice_email(self, to_email, invoice_number, pdf_path):
        """Send invoice via email"""
        business_name = self.settings.get('business_name', 'Business')
        subject = f"Invoice {invoice_number} from {business_name}"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="background-color: #2c3e50; color: white; padding: 20px; text-align: center;">
                <h2>{business_name}</h2>
                <p>{self.settings.get('business_address', '')}</p>
            </div>
            <div style="padding: 20px;">
                <h2>Invoice {invoice_number}</h2>
                <p>Dear Customer,</p>
                <p>Thank you for your business. Please find attached invoice {invoice_number} for your reference.</p>
                <br>
                <p><strong>Payment Instructions:</strong></p>
                <p>
                    Bank: {self.settings.get('bank_name', 'N/A')}<br>
                    Account Number: {self.settings.get('bank_account_number', 'N/A')}<br>
                    IFSC Code: {self.settings.get('bank_ifsc', 'N/A')}<br>
                    UPI ID: {self.settings.get('bank_upi_id', 'N/A')}
                </p>
                <br>
                <p>For any queries, please contact us at {self.settings.get('business_email', '')}</p>
                <br>
                <p>Best regards,<br>
                {business_name}</p>
            </div>
            <div style="background-color: #ecf0f1; padding: 10px; text-align: center; font-size: 12px;">
                <p>This is a computer generated invoice. No signature required.</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, body, pdf_path)