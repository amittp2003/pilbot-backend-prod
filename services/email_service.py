import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Email credentials
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

def sendEmail(recipient_email, user, response):
    try:
        # Validate email credentials
        if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
            raise Exception("Email credentials not configured. Please check .env file.")
        
        print(f"Attempting to send email to {recipient_email}...")
        print(f"Using email: {EMAIL_ADDRESS}")
        
        # Set up the server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        print("✓ Server login successful")
        
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = recipient_email
        msg['Subject'] = "Your Requested Information from Pillai College of Engineering"
        
        # Email body with better formatting
        body = f"""Hi {user},

Thank you for using Pilbot - Pillai College of Engineering's AI Assistant.

Here is the information you requested:

{response}

---
Best regards,
Pilbot - PCE AI Assistant
Pillai College of Engineering
"""
        msg.attach(MIMEText(body, 'plain'))
        print("✓ Email message created")
        
        # Send the email
        server.send_message(msg)
        print(f"✓ Email sent successfully to {recipient_email}")
        server.quit()

        return True
    except Exception as e:
        print(f"✗ Failed to send email. Error: {e}")
        raise e

# if __name__ == "__main__":
#     # Prompt for recipient email
#     recipient_email = input("Enter the recipient email address: ")
#     send_test_email(recipient_email)
