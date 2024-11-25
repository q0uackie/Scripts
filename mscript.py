import smtplib
import time
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, request

# Server Configuration
HEARTBEAT_TIMEOUT = 30  # 5 minutes in seconds
EMAIL_SENDER = "tobias.ober2008@gmail.com"
EMAIL_RECEIVER = "tobias.oberegger2008@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_PASSWORD = "hanf dllb hell slai"

# Heartbeat Tracking
last_heartbeat = time.time()

# Flask App Setup
app = Flask(__name__)

@app.route('/heartbeat', methods=['POST'])
def receive_heartbeat():
    global last_heartbeat
    last_heartbeat = time.time()
    return "Heartbeat received", 200

# Function to send an email notification
def send_email():
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Monitor-Status: Offline"
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    # Create the HTML email content
    html = f"""
    <html>
      <body>
        <div style='border: 1px solid #ddd; padding: 20px;'>
          <h2 style='color: #d9534f;'>Monitor-Status: Offline</h2>
          <p><strong>Monitor-Name:</strong> MacBook-Air-von-Tobias.local</p>
          <p><strong>Alias:</strong> Mein Alias</p>
          <p><strong>Standort:</strong> Büro</p>
          <p><strong>Bemerkung:</strong> Der Monitor scheint offline zu sein und hat sich seit über 5 Minuten nicht gemeldet.</p>
        </div>
      </body>
    </html>
    """
    msg.attach(MIMEText(html, 'html'))

    # Send the email
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to check for timeout
def monitor_status():
    global last_heartbeat
    while True:
        if time.time() - last_heartbeat > HEARTBEAT_TIMEOUT:
            send_email()
            time.sleep(HEARTBEAT_TIMEOUT)  # To prevent sending multiple emails
        time.sleep(1)

# Start the monitoring thread
monitor_thread = threading.Thread(target=monitor_status)
monitor_thread.daemon = True
monitor_thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
