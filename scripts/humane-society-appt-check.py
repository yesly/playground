from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Go to website
url = "https://app.qtrac.com/scheduler-execution?c-id=70b63f49-c6f1-4e03-9195-420105b2eb51&s-id=e7df69f1-3c63-499f-b92f-785339e07a37&type=AB&b-id=d29485ce-44cd-4127-9492-0504986dcee4"
driver.get(url)

wait = WebDriverWait(driver, 15)

# Select service
try:
    service_button = wait.until(EC.presence_of_element_located((
        By.XPATH,
        "//li[p[contains(., 'Cat Spay ($85) or Neuter ($85)')]]"
    )))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", service_button)
    driver.execute_script("arguments[0].click();", service_button)
    print("✅ Service option clicked!")
except Exception as e:
    raise RuntimeError(f"⚠️ Could not click the service option: {e}")

# Click on 'Continue' button
try:
    continue_button = wait.until(EC.presence_of_element_located((
        By.XPATH,
        "//input[@type='button' and @value='Continue']"
    )))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_button)
    driver.execute_script("arguments[0].click();", continue_button)
    print("✅ Continue button clicked!")
except Exception as e:
    raise RuntimeError(f"⚠️ Could not click Continue button: {e}")

# Check appointment message
is_appointment_available = False

wait = WebDriverWait(driver, 10)

try:
    no_timeslot_elem = wait.until(EC.presence_of_element_located((
        By.XPATH,
        "//p[contains(text(), 'There are no timeslots available')]"
    )))

    text = driver.execute_script("return arguments[0].innerText;", no_timeslot_elem)
    if "no timeslots available" in text.lower():
        print("⚠️ No available appointments.")
except Exception as e:
    print(f"✅ Appointments might be available.")
    is_appointment_available = True

driver.quit()

if is_appointment_available:
    # Send email
    sender_email = os.environ.get("SENDER_EMAIL_ADDRESS")
    sender_password = os.environ.get("SENDER_EMAIL_PASSWORD")
    receiver_email = os.environ.get("RECEIVER_EMAIL_ADDRESS")

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Humane Society Appointment Check"

    body = f"""
        <html>
          <body>
            <p>Appointments might be available: 
                <a href="{url}">Visit Website</a>
            </p>
          </body>
        </html>
        """
    message.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        print("✅ Email sent successfully!")
    except Exception as e:
        raise RuntimeError(f"⚠️ Could not send email: {e}")