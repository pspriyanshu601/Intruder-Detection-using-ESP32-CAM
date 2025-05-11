import time
import requests
import os
import smtplib
from email.message import EmailMessage
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 🔧 CONFIGURATION
WATCHED_FOLDER = r"C:\xampp\htdocs\ESP32CAM\captured_images"
API_ENDPOINT = "https://66ba-34-125-138-183.ngrok-free.app/identify"
TO_EMAIL = "21je0715@iitism.ac.in"
FROM_EMAIL = "ayushpersonalwork19@gmail.com"
EMAIL_PASSWORD = "denavlbofcxewpsc"  # Use Gmail App Password here

def send_intruder_alert(image_path):
    msg = EmailMessage()
    msg['Subject'] = "🚨 Intruder Alert Detected!"
    msg['From'] = FROM_EMAIL
    msg['To'] = TO_EMAIL
    msg.set_content("An intruder has been detected by the ESP32-CAM system. See the attached image.")

    with open(image_path, 'rb') as img:
        img_data = img.read()
        img_name = os.path.basename(image_path)
        msg.add_attachment(img_data, maintype='image', subtype='jpeg', filename=img_name)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(FROM_EMAIL, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print("📧 Intruder alert email sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

class ImageUploadHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        if event.src_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            print(f"📸 New image detected: {event.src_path}")
            time.sleep(1)  # Wait in case it's still being written

            try:
                with open(event.src_path, 'rb') as img_file:
                    files = {'image': (os.path.basename(event.src_path), img_file)}
                    response = requests.post(API_ENDPOINT, files=files)

                if response.status_code == 200:
                    print(f"✅ Uploaded {os.path.basename(event.src_path)} successfully.")
                    result = response.json()
                    print(result)
                    # 🔍 Check if intruder is detected
                    if result.get("found") == False and result.get("reason") != "No face detected":
                        print("🚨 Intruder detected! Sending email alert.")
                        send_intruder_alert(event.src_path)
                    else:
                        print("✅ No intruder detected.")
                else:
                    print(f"❌ Failed to upload {os.path.basename(event.src_path)}. Status: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Error processing file: {e}")

if __name__ == "__main__":
    event_handler = ImageUploadHandler()
    observer = Observer()
    observer.schedule(event_handler, path=WATCHED_FOLDER, recursive=False)
    observer.start()
    print(f"🚀 Watching folder: {WATCHED_FOLDER}")

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
