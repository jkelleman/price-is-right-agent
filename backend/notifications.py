import os
import aiosmtplib
from email.message import EmailMessage
from typing import List, Optional
import logging

from models import Alert, Item

logger = logging.getLogger(__name__)

class EmailNotifier:
    """
    Email notification service for price alerts
    
    Technical Decisions:
    - aiosmtplib: Async SMTP, non-blocking
    - HTML emails: Rich formatting for better UX
    - Environment config: Flexible SMTP provider (Gmail, SendGrid, AWS SES)
    - Graceful failure: Email errors don't crash the app
    - Batch sending: Group alerts to avoid spam
    
    Tradeoffs:
    - SMTP vs dedicated service (SendGrid API):
      SMTP is universal but slower; dedicated APIs are faster but vendor-locked
    - We choose SMTP for flexibility - users can use any provider
    """
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
        self.to_email = os.getenv("NOTIFICATION_EMAIL")  # User's email
        
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not configured - email notifications disabled")
            self.enabled = False
        else:
            self.enabled = True
    
    async def send_price_alert(self, item: Item, alert: Alert):
        """Send email notification for a price alert"""
        if not self.enabled or not self.to_email:
            logger.info("Email notifications disabled or no recipient configured")
            return
        
        subject = f"🔔 Price Alert: {item.name}"
        
        if alert.alert_type == "price_drop":
            html_body = self._create_price_drop_email(item, alert)
        elif alert.alert_type == "similar_item":
            html_body = self._create_similar_item_email(item, alert)
        else:
            html_body = f"<p>{alert.message}</p>"
        
        await self._send_email(subject, html_body)
    
    async def send_batch_alerts(self, alerts: List[tuple[Item, Alert]]):
        """Send multiple alerts in one email"""
        if not self.enabled or not self.to_email:
            return
        
        if not alerts:
            return
        
        subject = f"🔔 {len(alerts)} New Price Alerts"
        
        html_body = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                .alert { 
                    border: 1px solid #ddd; 
                    padding: 15px; 
                    margin: 10px 0; 
                    border-radius: 5px; 
                }
                .price-drop { background-color: #e8f5e9; }
                .similar-item { background-color: #e3f2fd; }
                .item-name { font-size: 18px; font-weight: bold; }
                .price { color: #2e7d32; font-size: 20px; font-weight: bold; }
                .link { color: #1976d2; text-decoration: none; }
            </style>
        </head>
        <body>
            <h2>Your Price Tracker Alerts</h2>
        """
        
        for item, alert in alerts:
            alert_class = "price-drop" if alert.alert_type == "price_drop" else "similar-item"
            html_body += f"""
            <div class="alert {alert_class}">
                <div class="item-name">{item.name}</div>
                <p>{alert.message}</p>
                <a href="{item.url}" class="link">View Item →</a>
            </div>
            """
        
        html_body += """
        </body>
        </html>
        """
        
        await self._send_email(subject, html_body)
    
    def _create_price_drop_email(self, item: Item, alert: Alert) -> str:
        """Create HTML email for price drop alert"""
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                           color: white; padding: 30px; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f5f5f5; padding: 30px; }}
                .price-box {{ background: white; padding: 20px; border-radius: 10px; 
                             margin: 20px 0; text-align: center; }}
                .price {{ color: #2e7d32; font-size: 36px; font-weight: bold; }}
                .button {{ background: #667eea; color: white; padding: 15px 30px; 
                          text-decoration: none; border-radius: 5px; display: inline-block; 
                          margin-top: 20px; }}
                .footer {{ background: #333; color: #aaa; padding: 20px; 
                          border-radius: 0 0 10px 10px; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Price Drop Alert!</h1>
                    <p>The item you're tracking has dropped to your target price</p>
                </div>
                <div class="content">
                    <h2>{item.name}</h2>
                    {f'<img src="{item.image_url}" style="max-width: 100%; border-radius: 10px;" />' if item.image_url else ''}
                    <div class="price-box">
                        <p>Current Price</p>
                        <div class="price">${item.current_price:.2f}</div>
                        {f'<p style="color: #666;">Target: ${item.target_price:.2f}</p>' if item.target_price else ''}
                    </div>
                    <p>{alert.message}</p>
                    <a href="{item.url}" class="button">View Item Now →</a>
                </div>
                <div class="footer">
                    <p>You're receiving this because you set up price tracking for this item.</p>
                    <p>Price Tracker - Smart Shopping Assistant</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_similar_item_email(self, item: Item, alert: Alert) -> str:
        """Create HTML email for similar item alert"""
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                           color: white; padding: 30px; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f5f5f5; padding: 30px; }}
                .button {{ background: #f5576c; color: white; padding: 15px 30px; 
                          text-decoration: none; border-radius: 5px; display: inline-block; 
                          margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💡 Better Alternative Found!</h1>
                    <p>We found a similar item at a better price</p>
                </div>
                <div class="content">
                    <h2>{item.name}</h2>
                    <p>{alert.message}</p>
                    <a href="{item.url}" class="button">View Original Item →</a>
                </div>
            </div>
        </body>
        </html>
        """
    
    async def _send_email(self, subject: str, html_body: str):
        """Send HTML email via SMTP"""
        try:
            message = EmailMessage()
            message["From"] = self.from_email
            message["To"] = self.to_email
            message["Subject"] = subject
            message.set_content("Please view this email in an HTML-compatible email client.")
            message.add_alternative(html_body, subtype="html")
            
            async with aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_tls=False
            ) as smtp:
                await smtp.connect()
                await smtp.starttls()
                await smtp.login(self.smtp_user, self.smtp_password)
                await smtp.send_message(message)
            
            logger.info(f"Email sent: {subject}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            # Don't raise - email failures shouldn't crash the app

# Global instance
email_notifier = EmailNotifier()
