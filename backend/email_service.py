import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# 📧 REAL EMAIL SERVICE
# ==========================================

def send_email(to_email: str, message: str):
    # Load credentials securely
    sender_email = os.getenv("EMAIL_USER")
    app_password = os.getenv("EMAIL_PASS")

    try:
        # Create the email structure
        msg = MIMEText(message)
        msg['Subject'] = 'Customer Support Response'
        msg['From'] = sender_email
        msg['To'] = to_email

        print("⏳ Connecting to Gmail server...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls() # Secure the connection
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ EMAIL SENT SUCCESSFULLY TO: {to_email}")
        return True
    except Exception as e:
        print("❌ Failed to send email:", e)
        return False