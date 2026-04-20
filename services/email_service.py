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
    
    def send_invoice_email(self, to_email, invoice_number, pdf_path):
        """Send invoice via email"""
        try:
            smtp_host = self.settings.get('smtp_host', '')
            smtp_port = int(self.settings.get('smtp_port', 587))
            smtp_user = self.settings.get('smtp_user', '')
            smtp_password = self.settings.get('smtp_password', '')
            from_email = self.settings.get('smtp_from_email', smtp_user)
            business_name = self.settings.get('business_name', 'Business')
            
            if not all([smtp_host, smtp_user, smtp_password]):
                return False, "SMTP settings not configured"
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = f"Invoice {invoice_number} from {business_name}"
            
            # Email body
            body = f"""
            Dear Customer,
            
            Please find attached invoice {invoice_number}.
            
            Thank you for your business!
            
            Regards,
            {business_name}
            """
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach PDF
            with open(pdf_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename=invoice_{invoice_number}.pdf')
                msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()
            
            return True, "Email sent successfully"
        
        except Exception as e:
            return False, f"Failed to send email: {str(e)}"