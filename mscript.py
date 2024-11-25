import smtplib
import time
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, request

# Server Configuration
HEARTBEAT_TIMEOUT = 30  # Timeout in seconds
EMAIL_SENDER = "tobias.ober2008@gmail.com"
EMAIL_RECEIVER = "tobias.oberegger2008@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_PASSWORD = "hanf dllb hell slai"  # Replace with your actual password or app-specific password

# Heartbeat Tracking
monitors = {}

# Flask App Setup
app = Flask(__name__)

@app.route('/heartbeat', methods=['POST'])
def receive_heartbeat():
    global monitors
    monitor_data = request.json
    monitor_name = monitor_data.get("monitor_name")
    alias = monitor_data.get("alias")
    location = monitor_data.get("location")

    if monitor_name:
        monitors[monitor_name] = {
            "last_heartbeat": time.time(),
            "alias": alias,
            "location": location,
            "offline": False
        }
    return "Heartbeat received", 200

# Function to send an email notification
def send_email(monitor_name, alias, location):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"Monitor-Status: Offline ({monitor_name})"
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    # Create the HTML email content
    html = f"""
    <html>
      <body>
        <div style='border: 1px solid #ddd; padding: 20px;'>
          <h2 style='color: #d9534f;'>Monitor-Status: Offline</h2>
          <p><strong>Monitor-Name:</strong> {monitor_name}</p>
          <p><strong>Alias:</strong> {alias}</p>
          <p><strong>Standort:</strong> {location}</p>
          <p><strong>Bemerkung:</strong> Der Monitor scheint offline zu sein und hat sich seit über 30 Sekunden nicht gemeldet.</p>
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
        print(f"Email sent successfully for monitor: {monitor_name}")
    except Exception as e:
        print(f"Failed to send email for monitor {monitor_name}: {e}")

# Function to check for timeout
def monitor_status():
    global monitors
    while True:
        current_time = time.time()
        for monitor_name, data in monitors.items():
            if current_time - data["last_heartbeat"] > HEARTBEAT_TIMEOUT:
                if not data["offline"]:
                    send_email(monitor_name, data["alias"], data["location"])
                    monitors[monitor_name]["offline"] = True
            else:
                monitors[monitor_name]["offline"] = False
        time.sleep(1)

# Start the monitoring thread
monitor_thread = threading.Thread(target=monitor_status)
monitor_thread.daemon = True
monitor_thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
