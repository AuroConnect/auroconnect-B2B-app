import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import secrets
import string

class EmailSender:
    """Email sender utility using AWS SES SMTP for partnership requests and notifications"""
    
    def __init__(self):
        # AWS SES SMTP configuration
        self.smtp_host = os.getenv('SMTP_HOST', 'email-smtp.us-east-1.amazonaws.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', 'AKIA2HVQ5B37BOPOZDX6')
        self.smtp_pass = os.getenv('SMTP_PASS', 'BPlPrOJGJDsf31A6tGFL42Vb9FtWTE+Awcti/AVchmdm')
        self.sender_email = os.getenv('SES_SENDER_EMAIL', 'noreply@easiehome.com')
        self.reply_to_email = os.getenv('SES_REPLY_TO_EMAIL', 'support@easiehome.com')
        
        # Test SMTP connection on initialization
        self._test_smtp_connection()
    
    def _test_smtp_connection(self):
        """Test SMTP connection on startup"""
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
            print(f"✅ SMTP connection successful to {self.smtp_host}")
        except Exception as e:
            print(f"⚠️  SMTP connection failed: {str(e)}")
            print("⚠️  Email sending may not work. Check your SMTP credentials.")
    
    def _generate_invite_token(self):
        """Generate a secure invite token"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    
    def _send_email(self, to_email, subject, html_body, reply_to=None):
        """Send email using AWS SES SMTP"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if reply_to:
                msg['Reply-To'] = reply_to
            else:
                msg['Reply-To'] = self.reply_to_email
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            
            print(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Email sending failed to {to_email}: {str(e)}")
            return False
    
    def send_partnership_invite(self, from_user, to_email, invite_token, message=""):
        """Send partnership invitation email with invite link"""
        try:
            # Generate invite link
            base_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
            invite_link = f"{base_url}/partnerships/invite/{invite_token}"
            
            subject = f"Partnership Invitation from {from_user.get('businessName', 'AuroMart Partner')}"
            
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                        <h1 style="margin: 0; font-size: 28px;">🤝 Partnership Invitation</h1>
                        <p style="margin: 10px 0 0 0; opacity: 0.9;">AuroMart B2B Platform</p>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                        <p style="font-size: 16px; margin-bottom: 20px;">Hello!</p>
                        
                        <p style="font-size: 16px; margin-bottom: 20px;">
                            <strong>{from_user.get('businessName', 'A Business Partner')}</strong> has invited you to establish a partnership on AuroMart.
                        </p>
                        
                        <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea;">
                            <h3 style="margin-top: 0; color: #667eea;">Partner Details:</h3>
                            <p><strong>Business:</strong> {from_user.get('businessName', 'N/A')}</p>
                            <p><strong>Role:</strong> {from_user.get('role', 'N/A').title()}</p>
                            <p><strong>Email:</strong> {from_user.get('email', 'N/A')}</p>
                            {f'<p><strong>Phone:</strong> {from_user.get("phoneNumber", "N/A")}</p>' if from_user.get('phoneNumber') else ''}
                        </div>
                        
                        {f'''
                        <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2196f3;">
                            <h3 style="margin-top: 0; color: #2196f3;">Message:</h3>
                            <p style="font-style: italic; margin: 0;">"{message}"</p>
                        </div>
                        ''' if message else ''}
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{invite_link}" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; display: inline-block; margin: 10px;">
                                ✅ Accept Partnership
                            </a>
                            <br>
                            <a href="{base_url}/partnerships/decline/{invite_token}" style="background: #f44336; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; display: inline-block; margin: 10px;">
                                ❌ Decline Partnership
                            </a>
                        </div>
                        
                        <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ffc107;">
                            <h4 style="margin-top: 0; color: #856404;">What happens next?</h4>
                            <ul style="margin: 0; padding-left: 20px;">
                                <li>Click "Accept Partnership" to establish the connection</li>
                                <li>You'll be able to see each other's products and services</li>
                                <li>Start doing business together on the platform</li>
                            </ul>
                        </div>
                        
                        <p style="font-size: 14px; color: #666; text-align: center; margin-top: 30px;">
                            This invitation will expire in 7 days.<br>
                            If you have any questions, please contact our support team.
                        </p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                        <p style="margin: 0; font-size: 12px; color: #666;">
                            © 2024 AuroMart B2B Platform. All rights reserved.<br>
                            This is an automated message from AuroMart B2B Platform.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return self._send_email(to_email, subject, html_body, reply_to=from_user.get('email'))
            
        except Exception as e:
            print(f"❌ Partnership invite email error: {str(e)}")
            return False
    
    def send_partnership_accepted(self, to_user, from_user):
        """Send partnership accepted notification"""
        try:
            subject = f"✅ Partnership Accepted - {from_user.get('businessName', 'Partner')}"
            
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #4caf50 0%, #45a049 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                        <h1 style="margin: 0; font-size: 28px;">🎉 Partnership Accepted!</h1>
                        <p style="margin: 10px 0 0 0; opacity: 0.9;">Your partnership is now active</p>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                        <p style="font-size: 16px; margin-bottom: 20px;">Great news! Your partnership request has been accepted.</p>
                        
                        <div style="background: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #4caf50;">
                            <h3 style="margin-top: 0; color: #2e7d32;">Partner Details:</h3>
                            <p><strong>Business:</strong> {from_user.get('businessName', 'N/A')}</p>
                            <p><strong>Role:</strong> {from_user.get('role', 'N/A').title()}</p>
                            <p><strong>Email:</strong> {from_user.get('email', 'N/A')}</p>
                        </div>
                        
                        <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2196f3;">
                            <h3 style="margin-top: 0; color: #1976d2;">What's Next?</h3>
                            <ul style="margin: 0; padding-left: 20px;">
                                <li>You can now see each other's products and services</li>
                                <li>Start placing orders and doing business together</li>
                                <li>Communicate through the platform's messaging system</li>
                                <li>Access shared analytics and reports</li>
                            </ul>
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{os.getenv('FRONTEND_URL', 'http://localhost:3000')}" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; display: inline-block;">
                                🚀 Go to AuroMart
                            </a>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                        <p style="margin: 0; font-size: 12px; color: #666;">
                            © 2024 AuroMart B2B Platform. All rights reserved.<br>
                            This is an automated message from AuroMart B2B Platform.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return self._send_email(to_user.get('email'), subject, html_body)
            
        except Exception as e:
            print(f"❌ Partnership accepted email error: {str(e)}")
            return False
    
    def send_partnership_declined(self, to_user, from_user, reason=""):
        """Send partnership declined notification"""
        try:
            subject = f"❌ Partnership Request Update - {from_user.get('businessName', 'Partner')}"
            
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                        <h1 style="margin: 0; font-size: 28px;">Partnership Request Update</h1>
                        <p style="margin: 10px 0 0 0; opacity: 0.9;">Your request has been declined</p>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                        <p style="font-size: 16px; margin-bottom: 20px;">Your partnership request has been declined.</p>
                        
                        <div style="background: #ffebee; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #f44336;">
                            <h3 style="margin-top: 0; color: #c62828;">Partner Details:</h3>
                            <p><strong>Business:</strong> {from_user.get('businessName', 'N/A')}</p>
                            <p><strong>Role:</strong> {from_user.get('role', 'N/A').title()}</p>
                            <p><strong>Email:</strong> {from_user.get('email', 'N/A')}</p>
                        </div>
                        
                        {f'''
                        <div style="background: #fff3e0; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ff9800;">
                            <h3 style="margin-top: 0; color: #e65100;">Reason:</h3>
                            <p style="font-style: italic; margin: 0;">"{reason}"</p>
                        </div>
                        ''' if reason else ''}
                        
                        <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2196f3;">
                            <h3 style="margin-top: 0; color: #1976d2;">Don't worry!</h3>
                            <p style="margin-bottom: 15px;">You can continue to explore other potential partners on AuroMart.</p>
                            <ul style="margin: 0; padding-left: 20px;">
                                <li>Browse the partner directory</li>
                                <li>Send invitations to other businesses</li>
                                <li>Connect with partners that match your needs</li>
                            </ul>
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/partners" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; display: inline-block;">
                                🔍 Find New Partners
                            </a>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                        <p style="margin: 0; font-size: 12px; color: #666;">
                            © 2024 AuroMart B2B Platform. All rights reserved.<br>
                            This is an automated message from AuroMart B2B Platform.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return self._send_email(to_user.get('email'), subject, html_body)
            
        except Exception as e:
            print(f"❌ Partnership declined email error: {str(e)}")
            return False

# Global email sender instance
email_sender = EmailSender()
